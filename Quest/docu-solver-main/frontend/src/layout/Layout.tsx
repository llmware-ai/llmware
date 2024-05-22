interface Props {
  className: string;
  children: React.ReactNode;
}
const Layout = ({ className, children }: Props) => {
  return <div className={`${className}`}>{children}</div>;
};

export default Layout;
