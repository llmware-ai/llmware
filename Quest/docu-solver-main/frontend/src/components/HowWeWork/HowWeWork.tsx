import { FaCloudUploadAlt } from "react-icons/fa";
import { BiSolidAnalyse } from "react-icons/bi";
import { IoChatbox } from "react-icons/io5";

const HowWeWork = () => {
  return (
    <div className="flex justify-center items-center flex-col">
      <h2 className="text-5xl m-10 w-full flex justify-center items-center">How it Work</h2>
      <div className="flex justify-center items-center text-2xl">
        <div className="flex justify-center items-center flex-col w-4/12">
          <div>
            <FaCloudUploadAlt className="text-5xl text-green-500" />
          </div>
          <div>Upload</div>
          <p className="text-gray-600 text-base my-5 px-16 text-center w-50%">
            Upload your study materials, including PDF documents, to the
            DocuSolver platform
          </p>
        </div>
        <div className="flex justify-center items-center flex-col w-4/12">
          <div>
            <BiSolidAnalyse className="text-5xl text-green-500" />
          </div>
          <div>Analysis</div>
          <p className="text-gray-600 text-base my-5 px-16 text-center w-50%">
            DocuSolver comprehensively analyzes your documents, extracting key
            information and identifying relevant questions.
          </p>
        </div>
        <div className="flex justify-center items-center flex-col w-4/12 ">
          <div>
            <IoChatbox className="text-5xl text-green-500" />
          </div>
          <div>Chat</div>
          <p className="text-gray-600 text-base my-5 px-16 text-center w-50%">
            Chat with DocuSolver to receive instant answers and explanations for
            the identified questions, enhancing your exam preparation.
          </p>
        </div>
      </div>
    </div>
  );
};

export default HowWeWork;
