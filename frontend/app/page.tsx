"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

const HomePage = () => {
  const router = useRouter();

  useEffect(() => {
    router.push("/main");
  }, [router]);

  return null; // or a loading spinner
};

export default HomePage;
