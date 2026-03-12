import React, { useEffect, useState } from "react";
import Head from "next/head";
import { useRouter } from "next/router";
import styles from "../styles/Dashboard.module.css";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

interface User {
  user_id: string;
  email: string;
  roles: string[];
}

interface Invoice {
  invoice_id: string;
  amount_due: number;
  status: string;
  hosted_invoice_url?: string;
}

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [usage, setUsage] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");
  const router = useRouter();

  // Helper to get JWT token from localStorage
  const getToken = () => {
    return localStorage.getItem("token");
  };

  useEffect(() => {
    const fetchUser = async () => {
      const token = getToken();
      if (!token) {
        router.push("/login");
        return;
      }
      try {
        const res = await fetch(`${API_BASE_URL}/auth/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (!res.ok) {
          throw new Error("Failed to fetch user info");
        }
        const data = await res.json();
        setUser(data);
      } catch (err) {
        setErrorMsg("Session expired or invalid. Please login again.");
        localStorage.removeItem("token");
        router.push("/login");
      }
    };

    const fetchInvoice = async () => {
      const token = getToken();
      if (!token) return;
      try {
        const res = await fetch(`${API_BASE_URL}/billing/invoice`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (!res.ok) {
          setInvoice(null);
          return;
        }
        const data = await res.json();
        setInvoice(data);
      } catch (err) {
        setInvoice(null);
      }
    };

    const fetchUsage = async () => {
      // For MVP, usage is simulated as a random value or can be fetched from backend if available
      // Here, we just set a static value for demonstration
      setUsage(Math.floor(Math.random() * 1000));
    };

    setLoading(true);
    Promise.all([fetchUser(), fetchInvoice(), fetchUsage()]).finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("token_type");
    router.push("/login");
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>Dashboard | python_aws_mvp</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <header className={styles.header}>
        <h1 className={styles.title}>Dashboard</h1>
        <button className={styles.logoutButton} onClick={handleLogout}>
          Logout
        </button>
      </header>
      <main className={styles.main}>
        {loading ? (
          <div className={styles.loading}>Loading...</div>
        ) : errorMsg ? (
          <div className={styles.error}>{errorMsg}</div>
        ) : (
          <>
            <section className={styles.userSection}>
              <h2>User Info</h2>
              <div className={styles.userInfo}>
                <div>
                  <strong>Email:</strong> {user?.email}
                </div>
                <div>
                  <strong>User ID:</strong> {user?.user_id}
                </div>
                <div>
                  <strong>Roles:</strong> {user?.roles.join(", ")}
                </div>
              </div>
            </section>
            <section className={styles.usageSection}>
              <h2>Usage Stats</h2>
              <div className={styles.usageInfo}>
                <div>
                  <strong>API Usage:</strong> {usage} units
                </div>
                <div>
                  <strong>File Uploads:</strong> {/* For MVP, not tracked */}
                  <span>Check Upload page for details</span>
                </div>
              </div>
            </section>
            <section className={styles.billingSection}>
              <h2>Billing Info</h2>
              {invoice ? (
                <div className={styles.billingInfo}>
                  <div>
                    <strong>Invoice ID:</strong> {invoice.invoice_id}
                  </div>
                  <div>
                    <strong>Amount Due:</strong> ${(invoice.amount_due / 100).toFixed(2)}
                  </div>
                  <div>
                    <strong>Status:</strong> {invoice.status}
                  </div>
                  {invoice.hosted_invoice_url && (
                    <div>
                      <a
                        href={invoice.hosted_invoice_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={styles.invoiceLink}
                      >
                        View Invoice
                      </a>
                    </div>
                  )}
                </div>
              ) : (
                <div className={styles.noInvoice}>No invoice found.</div>
              )}
            </section>
          </>
        )}
      </main>
      <footer className={styles.footer}>
        &copy; {new Date().getFullYear()} python_aws_mvp &mdash; Dashboard
      </footer>
    </div>
  );
}