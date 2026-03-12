import React from "react";
import Head from "next/head";
import Link from "next/link";
import styles from "../styles/Home.module.css";

const NAV_ITEMS = [
  { href: "/login", label: "Login / Register" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/upload", label: "Upload" },
  { href: "/billing", label: "Billing" },
];

export default function Home() {
  return (
    <div className={styles.container}>
      <Head>
        <title>python_aws_mvp | Cloud MVP Platform</title>
        <meta
          name="description"
          content="MVP platform with Python backend, AWS, Stripe billing, S3 uploads, and responsive Next.js/React frontend."
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <header className={styles.header}>
        <h1 className={styles.title}>python_aws_mvp</h1>
        <nav className={styles.nav}>
          {NAV_ITEMS.map((item) => (
            <Link key={item.href} href={item.href} className={styles.navLink}>
              {item.label}
            </Link>
          ))}
        </nav>
      </header>

      <main className={styles.main}>
        <section className={styles.hero}>
          <h2 className={styles.subtitle}>
            Rapidly deploy, scale, and manage your cloud MVP.
          </h2>
          <p className={styles.description}>
            Secure authentication, direct S3 uploads, metered Stripe billing, and full observability—all in a modern, responsive UI.
          </p>
          <div className={styles.ctaContainer}>
            <Link href="/login" className={styles.ctaButton}>
              Get Started
            </Link>
          </div>
        </section>

        <section className={styles.features}>
          <div className={styles.feature}>
            <h3>Authentication</h3>
            <p>Secure login and registration with JWT/OAuth2.</p>
          </div>
          <div className={styles.feature}>
            <h3>S3 Presigned Uploads</h3>
            <p>Fast, secure file uploads directly to AWS S3.</p>
          </div>
          <div className={styles.feature}>
            <h3>Metered Billing</h3>
            <p>Stripe integration for usage-based and subscription billing.</p>
          </div>
          <div className={styles.feature}>
            <h3>Observability</h3>
            <p>Integrated logging, monitoring, and error tracking.</p>
          </div>
        </section>
      </main>

      <footer className={styles.footer}>
        <span>
          &copy; {new Date().getFullYear()} python_aws_mvp &mdash; Powered by Next.js, React, AWS, Stripe
        </span>
        <Link href="/docs" className={styles.footerLink}>
          API Docs
        </Link>
      </footer>
    </div>
  );
}