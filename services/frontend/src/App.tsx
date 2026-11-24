import { useEffect } from "react";
import { RouterProvider } from "react-router-dom";

import { router } from "@/router";
import { useAuthStore } from "@/store/auth";

export default function App() {
  const loadMe = useAuthStore((s) => s.loadMe);

  useEffect(() => {
    void loadMe();
  }, [loadMe]);

  return <RouterProvider router={router} />;
}
