import { useState } from "react";
import { Button } from "../ui/button";
import { useToast } from "../ui/use-toast";

const NewsLetter = () => {
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    email: "",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;

    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    toast({
      variant: "newsletter",
      description:
        "Thanks for joining our community! Get ready for exciting updates. 🌟",
    });
  };

  return (
    <div id="newsletter" className="mt-20 flex justify-center items-center flex-col gap-12">
      <div className="text-5xl">
        Subscribe to Our
        <span className="text-green-500 font-extrabold"> Newsletter</span>
      </div>
      <p className="w-4/5 text-gray-500 text-center text-lg">
        Stay in the loop and never miss a beat! Subscribe to our newsletter to
        receive exclusive updates, insights, and exciting news directly to your
        inbox. Join our vibrant community of your enthusiasts and be part of the
        conversation.
      </p>
      <form className="mt-4" onSubmit={handleSubmit}>
        <div className="flex gap-10 justify-center items-center text-lg">
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Your Email"
            className=" py-2 px-4 w-64 border border-gray-300 rounded-md focus:outline-none focus:border-green-500"
            required
          />
          <Button className="py-6 px-3 text-lg bg-green-400 text-black hover:bg-green-500">
            Subscribe Now
          </Button>
        </div>
      </form>
    </div>
  );
};

export default NewsLetter;
