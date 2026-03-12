import React, { useEffect, useState } from "react";
import Head from "next/head";
import styles from "../styles/Billing.module.css";
import { useRouter } from "next/router";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

interface Subscription {
  stripe_subscription_id: string;
  plan_id: string;
}

interface Invoice {
  invoice_id: string;
  amount_due: number;
  status: string;
  hosted_invoice_url?: string;
}

export default function BillingPage() {
  const [planId, setPlanId] = useState<string>("");
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [usage, setUsage] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string>("");
  const [successMsg, setSuccessMsg] = useState<string>("");
  const router = useRouter();

  // Helper to get JWT token from localStorage
  const getToken = () => {
    return localStorage.getItem("token");
  };

  useEffect(() => {
    const fetchSubscription = async () => {
      const token = getToken();
      if (!token) {
        router.push("/login");
        return;
      }
      // For MVP, we assume subscription info is not persisted, so we skip fetching
      // In production, you would fetch from backend
      setSubscription(null);
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
      setUsage(Math.floor(Math.random() * 1000));
    };

    setLoading(true);
    Promise.all([fetchSubscription(), fetchInvoice(), fetchUsage()]).finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleCreateSubscription = async () => {
    setErrorMsg("");
    setSuccessMsg("");
    const token = getToken();
    if (!token) {
      router.push("/login");
      return;
    }
    if (!planId) {
      setErrorMsg("Please enter a plan ID.");
      return;
    }
    try {
      const res = await fetch(`${API_BASE_URL}/billing/create-subscription`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ plan_id: planId }),
      });
      const data = await res.json();
      if (!res.ok) {
        setErrorMsg(data.detail || "Failed to create subscription.");
        return;
      }
      setSubscription({ stripe_subscription_id: data.stripe_subscription_id, plan_id: planId });
      setSuccessMsg("Subscription created successfully.");
    } catch (err) {
      setErrorMsg("Network error during subscription creation.");
    }
  };

  const handleMeterUsage = async () => {
    setErrorMsg("");
    setSuccessMsg("");
    const token = getToken();
    if (!token) {
      router.push("/login");
      return;
    }
    try {
      const usageValue = Math.floor(Math.random() * 100) + 1; // Simulate usage
      const res = await fetch(`${API_BASE_URL}/billing/meter-usage`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ usage: usageValue }),
      });
      const data = await res.json();
      if (!res.ok) {
        setErrorMsg(data.detail || "Failed to record usage.");
        return;
      }
      setUsage((prev) => prev + usageValue);
      setSuccessMsg(`Usage recorded: ${usageValue} units.`);
    } catch (err) {
      setErrorMsg("Network error during usage metering.");
    }
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>Billing | python_aws_mvp</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <header className={styles.header}>
        <h1 className={styles.title}>Billing</h1>
      </header>
      <main className={styles.main}>
        {loading ? (
          <div className={styles.loading}>Loading...</div>
        ) : (
          <>
            <section className={styles.subscriptionSection}>
              <h2>Subscription</h2>
              {subscription ? (
                <div className={styles.subscriptionInfo}>
                  <div>
                    <strong>Subscription ID:</strong> {subscription.stripe_subscription_id}
                  </div>
                  <div>
                    <strong>Plan ID:</strong> {subscription.plan_id}
                  </div>
                </div>
              ) : (
                <div className={styles.createSubscription}>
                  <input
                    type="text"
                    className={styles.input}
                    placeholder="Enter Stripe Plan ID"
                    value={planId}
                    onChange={(e) => setPlanId(e.target.value)}
                  />
                  <button
                    className={styles.button}
                    onClick={handleCreateSubscription}
                  >
                    Create Subscription
                  </button>
                </div>
              )}
            </section>
            <section className={styles.usageSection}>
              <h2>Metered Usage</h2>
              <div className={styles.usageInfo}>
                <div>
                  <strong>Current Usage:</strong> {usage} units
                </div>
                <button
                  className={styles.button}
                  onClick={handleMeterUsage}
                >
                  Simulate Usage
                </button>
              </div>
            </section>
            <section className={styles.invoiceSection}>
              <h2>Latest Invoice</h2>
              {invoice ? (
                <div className={styles.invoiceInfo}>
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
            {errorMsg && <div className={styles.error}>{errorMsg}</div>}
            {successMsg && <div className={styles.success}>{successMsg}</div>}
          </>
        )}
      </main>
      <footer className={styles.footer}>
        &copy; {new Date().getFullYear()} python_aws_mvp &mdash; Billing
      </footer>
    </div>
  );
}