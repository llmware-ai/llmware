import logo from "../../assets/images/logo.png";

const Header = () => {
  return (
    <div className="flex justify-between items-center py-6 ">
      <div className="w-16">
        <a href="/">
          <img src={logo} alt="Logo" />
        </a>
      </div>
      <div className="flex justify-center items-center gap-10 text-base">
        <div className="cursor-pointer hover:text-green-500">Home</div>
        <div className="cursor-pointer hover:text-green-500"><a href="/">About</a></div>
        <div className="cursor-pointer hover:text-green-500"><a href="/#newsletter">Newsletter</a></div>
        <div className="cursor-pointer hover:text-green-500"><a href="/#FAQ">FAQ</a></div>
        <div className="cursor-pointer hover:text-green-500"><a href="/author">Author</a></div>
      </div>
      <a
        href="https://github.com/thapasusheel/docu-solver"
        className="px-6 py-2 bg-black text-white font-semibold tracking-widest rounded-lg text-base cursor-pointer hover:bg-green-500 hover:text-black"
      >
        Github
      </a>
    </div>
  );
};

export default Header;
