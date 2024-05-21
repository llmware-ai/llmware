
import {
  createBrowserRouter,
  RouterProvider, Outlet
} from "react-router-dom";

import Home from './pages/Home'
import Navbar from './components/NavBar'
import Footer from './components/Footer'
import AboutUs from "./pages/AboutUs";
import ContactUs from "./pages/ContactUs";
import Hero from "./components/Hero";
import NameCardPage from "./pages/NameCardPage";

const Layout = () => {
  return (
    <>
      <Navbar />
      <Outlet />
      <Footer />
    </>
  );
}
const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        path: '/',
        element: <Hero />
      },
      {
        path: '/home',
        element: <Home />
      },
      {
        path: '/about',
        element: <AboutUs />
      },
      {
        path: '/contact-us',
        element: <ContactUs />
      },
      {
        path : '/name-cards',
        element: <NameCardPage/>
      }
    ]
  },

]);


function App() {
  return (
    <div className="app">

        <RouterProvider router={router} />

    </div>
  );
}



export default App;
