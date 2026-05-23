import { assert } from 'console'
import util from 'util'
import * as session from 'express-session'
import {
  Collection,
  MongoClient,
  MongoClientOptions,
  WriteConcernSettings,
} from 'mongodb'
import Debug from 'debug'
import Kruptein from 'kruptein'

const debug = Debug('connect-mongo')

export type CryptoOptions = {
  secret: false | string
  algorithm?: string
  hashing?: string
  encodeas?: string
  key_size?: number
  iv_size?: number
  at_size?: number
}

export type ConnectMongoOptions = {
  mongoUrl?: string
  clientPromise?: Promise<MongoClient>
  client?: MongoClient
  collectionName?: string
  mongoOptions?: MongoClientOptions
  dbName?: string
  ttl?: number
  touchAfter?: number
  stringify?: boolean
  createAutoRemoveIdx?: boolean
  autoRemove?: 'native' | 'interval' | 'disabled'
  autoRemoveInterval?: number
  // FIXME: remove those any
  serialize?: (a: any) => any
  unserialize?: (a: any) => any
  writeOperationOptions?: WriteConcernSettings
  transformId?: (a: any) => any
  crypto?: CryptoOptions
}

type ConcretCryptoOptions = Required<CryptoOptions>

type ConcretConnectMongoOptions = {
  mongoUrl?: string
  clientPromise?: Promise<MongoClient>
  client?: MongoClient
  collectionName: string
  mongoOptions: MongoClientOptions
  dbName?: string
  ttl: number
  createAutoRemoveIdx?: boolean
  autoRemove: 'native' | 'interval' | 'disabled'
  autoRemoveInterval: number
  touchAfter: number
  stringify: boolean
  // FIXME: remove those any
  serialize?: (a: any) => any
  unserialize?: (a: any) => any
  writeOperationOptions?: WriteConcernSettings
  transformId?: (a: any) => any
  // FIXME: remove above any
  crypto: ConcretCryptoOptions
}

type InternalSessionType = {
  _id: string
  session: any
  expires?: Date
  lastModified?: Date
}

// eslint-disable-next-line @typescript-eslint/no-empty-function
const noop = () => {}
const unit: <T>(a: T) => T = (a) => a

function defaultSerializeFunction(
  session: session.SessionData
): session.SessionData {
  // Copy each property of the session to a new object
  const obj = {}
  let prop
  for (prop in session) {
    if (prop === 'cookie') {
      // Convert the cookie instance to an object, if possible
      // This gets rid of the duplicate object under session.cookie.data property
      // @ts-ignore FIXME:
      obj.cookie = session.cookie.toJSON
        ? // @ts-ignore FIXME:
          session.cookie.toJSON()
        : session.cookie
    } else {
      // @ts-ignore FIXME:
      obj[prop] = session[prop]
    }
  }

  return obj as session.SessionData
}

function computeTransformFunctions(options: ConcretConnectMongoOptions) {
  if (options.serialize || options.unserialize) {
    return {
      serialize: options.serialize || defaultSerializeFunction,
      unserialize: options.unserialize || unit,
    }
  }

  if (options.stringify === false) {
    return {
      serialize: defaultSerializeFunction,
      unserialize: unit,
    }
  }
  // Default case
  return {
    serialize: JSON.stringify,
    unserialize: JSON.parse,
  }
}

export default class MongoStore extends session.Store {
  private clientP: Promise<MongoClient>
  private crypto: Kruptein | null = null
  private timer?: NodeJS.Timeout
  collectionP: Promise<Collection<InternalSessionType>>
  private options: ConcretConnectMongoOptions
  // FIXME: remvoe any
  private transformFunctions: {
    serialize: (a: any) => any
    unserialize: (a: any) => any
  }

  constructor({
    collectionName = 'sessions',
    ttl = 1209600,
    mongoOptions = {},
    autoRemove = 'native',
    autoRemoveInterval = 10,
    touchAfter = 0,
    stringify = true,
    crypto,
    ...required
  }: ConnectMongoOptions) {
    super()
    debug('create MongoStore instance')
    const options: ConcretConnectMongoOptions = {
      collectionName,
      ttl,
      mongoOptions,
      autoRemove,
      autoRemoveInterval,
      touchAfter,
      stringify,
      crypto: {
        ...{
          secret: false,
          algorithm: 'aes-256-gcm',
          hashing: 'sha512',
          encodeas: 'base64',
          key_size: 32,
          iv_size: 16,
          at_size: 16,
        },
        ...crypto,
      },
      ...required,
    }
    // Check params
    assert(
      options.mongoUrl || options.clientPromise || options.client,
      'You must provide either mongoUrl|clientPromise|client in options'
    )
    assert(
      options.createAutoRemoveIdx === null ||
        options.createAutoRemoveIdx === undefined,
      'options.createAutoRemoveIdx has been reverted to autoRemove and autoRemoveInterval'
    )
    assert(
      !options.autoRemoveInterval || options.autoRemoveInterval <= 71582,
      /* (Math.pow(2, 32) - 1) / (1000 * 60) */ 'autoRemoveInterval is too large. options.autoRemoveInterval is in minutes but not seconds nor mills'
    )
    this.transformFunctions = computeTransformFunctions(options)
    let _clientP: Promise<MongoClient>
    if (options.mongoUrl) {
      _clientP = MongoClient.connect(options.mongoUrl, options.mongoOptions)
    } else if (options.clientPromise) {
      _clientP = options.clientPromise
    } else if (options.client) {
      _clientP = Promise.resolve(options.client)
    } else {
      throw new Error('Cannot init client. Please provide correct options')
    }
    assert(!!_clientP, 'Client is null|undefined')
    this.clientP = _clientP
    this.options = options
    this.collectionP = _clientP.then(async (con) => {
      const collection = con
        .db(options.dbName)
        .collection<InternalSessionType>(options.collectionName)
      await this.setAutoRemove(collection)
      return collection
    })
    if (options.crypto.secret) {
      this.crypto = require('kruptein')(options.crypto)
    }
  }

  static create(options: ConnectMongoOptions): MongoStore {
    return new MongoStore(options)
  }

  private setAutoRemove(
    collection: Collection<InternalSessionType>
  ): Promise<unknown> {
    const removeQuery = () => ({
      expires: {
        $lt: new Date(),
      },
    })
    switch (this.options.autoRemove) {
      case 'native':
        debug('Creating MongoDB TTL index')
        return collection.createIndex(
          { expires: 1 },
          {
            background: true,
            expireAfterSeconds: 0,
          }
        )
      case 'interval':
        debug('create Timer to remove expired sessions')
        this.timer = setInterval(
          () =>
            collection.deleteMany(removeQuery(), {
              writeConcern: {
                w: 0,
                j: false,
              },
            }),
          this.options.autoRemoveInterval * 1000 * 60
        )
        this.timer.unref()
        return Promise.resolve()
      case 'disabled':
      default:
        return Promise.resolve()
    }
  }

  private computeStorageId(sessionId: string) {
    if (
      this.options.transformId &&
      typeof this.options.transformId === 'function'
    ) {
      return this.options.transformId(sessionId)
    }
    return sessionId
  }

  /**
   * promisify and bind the `this.crypto.get` function.
   * Please check !!this.crypto === true before using this getter!
   */
  private get cryptoGet() {
    if (!this.crypto) {
      throw new Error('Check this.crypto before calling this.cryptoGet!')
    }
    return util.promisify(this.crypto.get).bind(this.crypto)
  }

  /**
   * Decrypt given session data
   * @param session session data to be decrypt. Mutate the input session.
   */
  private async decryptSession(
    session: session.SessionData | undefined | null
  ) {
    if (this.crypto && session) {
      const plaintext = await this.cryptoGet(
        this.options.crypto.secret as string,
        session.session
      ).catch((err) => {
        throw new Error(err)
      })
      // @ts-ignore
      session.session = JSON.parse(plaintext)
    }
  }

  /**
   * Get a session from the store given a session ID (sid)
   * @param sid session ID
   */
  get(
    sid: string,
    callback: (err: any, session?: session.SessionData | null) => void
  ): void {
    ;(async () => {
      try {
        debug(`MongoStore#get=${sid}`)
        const collection = await this.collectionP
        const session = await collection.findOne({
          _id: this.computeStorageId(sid),
          $or: [
            { expires: { $exists: false } },
            { expires: { $gt: new Date() } },
          ],
        })
        if (this.crypto && session) {
          await this.decryptSession(
            session as unknown as session.SessionData
          ).catch((err) => callback(err))
        }
        const s =
          session && this.transformFunctions.unserialize(session.session)
        if (this.options.touchAfter > 0 && session?.lastModified) {
          s.lastModified = session.lastModified
        }
        this.emit('get', sid)
        callback(null, s === undefined ? null : s)
      } catch (error) {
        callback(error)
      }
    })()
  }

  /**
   * Upsert a session into the store given a session ID (sid) and session (session) object.
   * @param sid session ID
   * @param session session object
   */
  set(
    sid: string,
    session: session.SessionData,
    callback: (err: any) => void = noop
  ): void {
    ;(async () => {
      try {
        debug(`MongoStore#set=${sid}`)
        // Removing the lastModified prop from the session object before update
        // @ts-ignore
        if (this.options.touchAfter > 0 && session?.lastModified) {
          // @ts-ignore
          delete session.lastModified
        }
        const s: InternalSessionType = {
          _id: this.computeStorageId(sid),
          session: this.transformFunctions.serialize(session),
        }
        // Expire handling
        if (session?.cookie?.expires) {
          s.expires = new Date(session.cookie.expires)
        } else {
          // If there's no expiration date specified, it is
          // browser-session cookie or there is no cookie at all,
          // as per the connect docs.
          //
          // So we set the expiration to two-weeks from now
          // - as is common practice in the industry (e.g Django) -
          // or the default specified in the options.
          s.expires = new Date(Date.now() + this.options.ttl * 1000)
        }
        // Last modify handling
        if (this.options.touchAfter > 0) {
          s.lastModified = new Date()
        }
        if (this.crypto) {
          const cryptoSet = util.promisify(this.crypto.set).bind(this.crypto)
          const data = await cryptoSet(
            this.options.crypto.secret as string,
            s.session
          ).catch((err) => {
            throw new Error(err)
          })
          s.session = data as unknown as session.SessionData
        }
        const collection = await this.collectionP
        const rawResp = await collection.updateOne(
          { _id: s._id },
          { $set: s },
          {
            upsert: true,
            writeConcern: this.options.writeOperationOptions,
          }
        )
        if (rawResp.upsertedCount > 0) {
          this.emit('create', sid)
        } else {
          this.emit('update', sid)
        }
        this.emit('set', sid)
      } catch (error) {
        return callback(error)
      }
      return callback(null)
    })()
  }

  touch(
    sid: string,
    session: session.SessionData & { lastModified?: Date },
    callback: (err: any) => void = noop
  ): void {
    ;(async () => {
      try {
        debug(`MongoStore#touch=${sid}`)
        const updateFields: {
          lastModified?: Date
          expires?: Date
          session?: session.SessionData
        } = {}
        const touchAfter = this.options.touchAfter * 1000
        const lastModified = session.lastModified
          ? session.lastModified.getTime()
          : 0
        const currentDate = new Date()

        // If the given options has a touchAfter property, check if the
        // current timestamp - lastModified timestamp is bigger than
        // the specified, if it's not, don't touch the session
        if (touchAfter > 0 && lastModified > 0) {
          const timeElapsed = currentDate.getTime() - lastModified
          if (timeElapsed < touchAfter) {
            debug(`Skip touching session=${sid}`)
            return callback(null)
          }
          updateFields.lastModified = currentDate
        }

        if (session?.cookie?.expires) {
          updateFields.expires = new Date(session.cookie.expires)
        } else {
          updateFields.expires = new Date(Date.now() + this.options.ttl * 1000)
        }
        const collection = await this.collectionP
        const rawResp = await collection.updateOne(
          { _id: this.computeStorageId(sid) },
          { $set: updateFields },
          { writeConcern: this.options.writeOperationOptions }
        )
        if (rawResp.matchedCount === 0) {
          return callback(new Error('Unable to find the session to touch'))
        } else {
          this.emit('touch', sid, session)
          return callback(null)
        }
      } catch (error) {
        return callback(error)
      }
    })()
  }

  /**
   * Get all sessions in the store as an array
   */
  all(
    callback: (
      err: any,
      obj?:
        | session.SessionData[]
        | { [sid: string]: session.SessionData }
        | null
    ) => void
  ): void {
    ;(async () => {
      try {
        debug('MongoStore#all()')
        const collection = await this.collectionP
        const sessions = collection.find({
          $or: [
            { expires: { $exists: false } },
            { expires: { $gt: new Date() } },
          ],
        })
        const results: session.SessionData[] = []
        for await (const session of sessions) {
          if (this.crypto && session) {
            await this.decryptSession(session as unknown as session.SessionData)
          }
          results.push(this.transformFunctions.unserialize(session.session))
        }
        this.emit('all', results)
        callback(null, results)
      } catch (error) {
        callback(error)
      }
    })()
  }

  /**
   * Destroy/delete a session from the store given a session ID (sid)
   * @param sid session ID
   */
  destroy(sid: string, callback: (err: any) => void = noop): void {
    debug(`MongoStore#destroy=${sid}`)
    this.collectionP
      .then((colleciton) =>
        colleciton.deleteOne(
          { _id: this.computeStorageId(sid) },
          { writeConcern: this.options.writeOperationOptions }
        )
      )
      .then(() => {
        this.emit('destroy', sid)
        callback(null)
      })
      .catch((err) => callback(err))
  }

  /**
   * Get the count of all sessions in the store
   */
  length(callback: (err: any, length: number) => void): void {
    debug('MongoStore#length()')
    this.collectionP
      .then((collection) => collection.countDocuments())
      .then((c) => callback(null, c))
      // @ts-ignore
      .catch((err) => callback(err))
  }

  /**
   * Delete all sessions from the store.
   */
  clear(callback: (err: any) => void = noop): void {
    debug('MongoStore#clear()')
    this.collectionP
      .then((collection) => collection.drop())
      .then(() => callback(null))
      .catch((err) => callback(err))
  }

  /**
   * Close database connection
   */
  close(): Promise<void> {
    debug('MongoStore#close()')
    return this.clientP.then((c) => c.close())
  }
}
