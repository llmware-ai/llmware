import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth, db } from '../../../firebase';
import { signInWithEmailAndPassword, createUserWithEmailAndPassword } from 'firebase/auth';
import { doc, getDoc, setDoc } from 'firebase/firestore';
import { CUSTOMER_SERVICE_EMAILS } from './authUtils';
import ChatWidget from './ChatWidget';
import { X } from 'lucide-react';

const AuthRoute = ({ onClose }) => {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // Check if customer service credentials
      const isCustomerService = CUSTOMER_SERVICE_EMAILS.some(
        (cs) => cs.email.toLowerCase() === email.toLowerCase()
      );

      if (isCustomerService) {
        // Handle customer service login with provided password
        try {
          const userCredential = await signInWithEmailAndPassword(auth, email, password);
          if (userCredential) {
            navigate('/dashboard/service-dashboard');
            onClose();
          }
        } catch (error) {
          setError('Invalid Service Credentials');
        }
        setIsLoading(false);
        return;
      }

      // Handle regular user
      const userRef = doc(db, 'users', email.toLowerCase());
      const userDoc = await getDoc(userRef);

      if (!userDoc.exists()) {
        // Create new user account
        try {
          await createUserWithEmailAndPassword(auth, email, "123456");
          // Store user data in Firestore
          await setDoc(userRef, {
            email: email.toLowerCase(),
            name: name || '',
            chatId: `chat_${email.toLowerCase()}`,
            createdAt: new Date(),
            lastActive: new Date(),
          });
          setIsAuthenticated(true);
        } catch (error) {
          throw error;
        }
      } else {
        // User exists, try to sign in
        try {
          await signInWithEmailAndPassword(auth, email, "123456");
          // Update last active timestamp
          await setDoc(userRef, {
            lastActive: new Date(),
            name: name || userDoc.data().name || '', // Update name if provided
          }, { merge: true });
          setIsAuthenticated(true);
        } catch (error) {
          throw error;
        }
      }
    } catch (error) {
      console.error('Auth error:', error);
      switch (error.code) {
        case 'auth/invalid-email':
          setError('Invalid email address');
          break;
        case 'auth/email-already-in-use':
          setError('This email is already in use');
          break;
        case 'auth/invalid-credential':
          setError('Invalid credentials. Please try again.');
          break;
        case 'auth/too-many-requests':
          setError('Too many attempts. Please try again later.');
          break;
        default:
          setError('Authentication failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (isAuthenticated) {
    return <ChatWidget userEmail={email} userName={name} autoOpen={true} />;
  }

  return (
    <div className="w-80 bg-white rounded-lg shadow-xl">
      <div className="flex justify-between items-center p-4 bg-blue-600 text-white rounded-t-lg">
        <div className="flex items-center space-x-1">
          <h3 className="font-semibold">Enter Details to Continue Chat</h3>
        </div>
        <button onClick={onClose} className="text-white hover:text-gray-200">
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="p-4">
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full p-2 border rounded focus:ring-blue-500 focus:border-blue-500"
              placeholder="Name (Optional)"
            />
          </div>
          <div>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-2 border rounded focus:ring-blue-500 focus:border-blue-500"
              placeholder="Email"
              required
            />
          </div>
          {CUSTOMER_SERVICE_EMAILS.some(
            (cs) => cs.email.toLowerCase() === email.toLowerCase()
          ) && (
            <div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full p-2 border rounded focus:ring-blue-500 focus:border-blue-500"
                placeholder="Password"
                required
                minLength="6"
              />
            </div>
          )}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? 'Loading...' : 'Continue'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AuthRoute;