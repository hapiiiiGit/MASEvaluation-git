import React, { useState } from "react";
import styles from "../styles/AuthForm.module.css";
import { useRouter } from "next/router";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

type AuthMode = "login" | "register";

interface AuthFormProps {
  initialMode?: AuthMode;
  onAuthSuccess?: (token: string, tokenType: string) => void;
}

const AuthForm: React.FC<AuthFormProps> = ({ initialMode = "login", onAuthSuccess }) => {
  const [mode, setMode] = useState<AuthMode>(initialMode);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");

    try {
      let response;
      if (mode === "login") {
        // FastAPI expects form data for login
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);

        response = await fetch(`${API_BASE_URL}/auth/login`, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: formData.toString(),
        });
      } else {
        // Registration expects JSON
        response = await fetch(`${API_BASE_URL}/auth/register`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email, password }),
        });
      }

      const data = await response.json();

      if (!response.ok) {
        setErrorMsg(data.detail || "Authentication failed.");
        setLoading(false);
        return;
      }

      // Save JWT token to localStorage
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("token_type", data.token_type);

      if (onAuthSuccess) {
        onAuthSuccess(data.access_token, data.token_type);
      }

      // Redirect to dashboard
      router.push("/dashboard");
    } catch (err) {
      setErrorMsg("Network error. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className={styles.formWrapper}>
      <h2 className={styles.title}>
        {mode === "login" ? "Login" : "Register"}
      </h2>
      <form className={styles.form} onSubmit={handleSubmit}>
        <label htmlFor="email" className={styles.label}>
          Email
        </label>
        <input
          id="email"
          type="email"
          className={styles.input}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoComplete="email"
          disabled={loading}
        />

        <label htmlFor="password" className={styles.label}>
          Password
        </label>
        <input
          id="password"
          type="password"
          className={styles.input}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          autoComplete={mode === "login" ? "current-password" : "new-password"}
          disabled={loading}
        />

        {errorMsg && <div className={styles.error}>{errorMsg}</div>}

        <button
          type="submit"
          className={styles.button}
          disabled={loading}
        >
          {loading
            ? mode === "login"
              ? "Logging in..."
              : "Registering..."
            : mode === "login"
            ? "Login"
            : "Register"}
        </button>
      </form>

      <div className={styles.toggle}>
        {mode === "login" ? (
          <>
            <span>Don't have an account?</span>
            <button
              className={styles.linkButton}
              onClick={() => setMode("register")}
              disabled={loading}
              type="button"
            >
              Register
            </button>
          </>
        ) : (
          <>
            <span>Already have an account?</span>
            <button
              className={styles.linkButton}
              onClick={() => setMode("login")}
              disabled={loading}
              type="button"
            >
              Login
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default AuthForm;