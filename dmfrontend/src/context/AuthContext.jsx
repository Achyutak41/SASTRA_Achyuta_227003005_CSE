import {
  createContext,
  useContext,
  useEffect,
  useState
} from "react";

import authService from "../services/authService";


const AuthContext =
  createContext(null);


export function AuthProvider({
  children
}) {
  const [user, setUser] =
    useState(null);

  const [
    isAuthenticated,
    setIsAuthenticated
  ] = useState(false);

  const [loading, setLoading] =
    useState(true);


  useEffect(() => {
    const token =
      localStorage.getItem(
        "autosar_token"
      );

    if (!token) {
      setLoading(false);
      return;
    }


    const restoreSession =
      async () => {
        try {
          const response =
            await authService.getCurrentUser();

          const currentUser =
            response.user;

          localStorage.setItem(
            "autosar_user",
            JSON.stringify(
              currentUser
            )
          );

          setUser(currentUser);
          setIsAuthenticated(true);

        } catch (error) {
          localStorage.removeItem(
            "autosar_user"
          );

          localStorage.removeItem(
            "autosar_token"
          );

          setUser(null);
          setIsAuthenticated(false);

        } finally {
          setLoading(false);
        }
      };


    restoreSession();

  }, []);


  const login = async (
    email,
    password
  ) => {
    if (!email || !password) {
      throw new Error(
        "Email and password are required."
      );
    }


    const response =
      await authService.login(
        email,
        password
      );


    const currentUser =
      response.user;

    const token =
      response.token;


    if (!token) {
      throw new Error(
        "Login succeeded, but no authentication token was returned."
      );
    }


    localStorage.setItem(
      "autosar_user",
      JSON.stringify(
        currentUser
      )
    );


    localStorage.setItem(
      "autosar_token",
      token
    );


    setUser(currentUser);
    setIsAuthenticated(true);


    return currentUser;
  };


  const register = async (
    name,
    email,
    password
  ) => {
    if (
      !name ||
      !email ||
      !password
    ) {
      throw new Error(
        "All fields are required."
      );
    }


    const response =
      await authService.register(
        name,
        email,
        password
      );


    const currentUser =
      response.user;

    const token =
      response.token;


    if (!token) {
      throw new Error(
        "Registration succeeded, but no authentication token was returned."
      );
    }


    localStorage.setItem(
      "autosar_user",
      JSON.stringify(
        currentUser
      )
    );


    localStorage.setItem(
      "autosar_token",
      token
    );


    setUser(currentUser);
    setIsAuthenticated(true);


    return currentUser;
  };


  const logout = async () => {
    try {
      const token =
        localStorage.getItem(
          "autosar_token"
        );

      if (token) {
        await authService.logout();
      }

    } catch (error) {
      // Clear the local session
      // even if backend logout fails.
    }


    localStorage.removeItem(
      "autosar_user"
    );

    localStorage.removeItem(
      "autosar_token"
    );


    setUser(null);
    setIsAuthenticated(false);
  };


  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        loading,
        login,
        register,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}


export function useAuthContext() {
  return useContext(
    AuthContext
  );
}