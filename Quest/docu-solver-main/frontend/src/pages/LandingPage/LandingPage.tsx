import Layout from "@/layout/Layout";
import Header from "@/components/Header";
import Hero from "@/components/Hero/Hero";
import Footer from "@/components/Footer";
import FAQ from "@/components/FAQ";
import NewsLetter from "@/components/NewsLetter";
import HowWeWork from "@/components/HowWeWork";

const LandingPage = () => {
  return (
    <>
      <Layout className="px-64">
        <Header />
        <Hero />
        <HowWeWork />
        <NewsLetter />
        <FAQ />
      </Layout>
      <Footer />
    </>
  );
};

export default LandingPage;
