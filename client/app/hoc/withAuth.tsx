import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export function withAuth<P extends object = object>(
  WrappedComponent: React.ComponentType<P>
) {
  return function AuthGuard(props: P) {
    const router = useRouter();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
      const token = localStorage.getItem("token");

      if (!token) {
        router.push("/");
      } else {
        setLoading(false);
      }
    }, [router]);

    if (loading) {
      return <div> </div>;
    }

    return <WrappedComponent {...props} />;
  };
}