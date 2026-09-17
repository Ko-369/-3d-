import type { Metadata, Viewport } from "next";
import { notFound } from "next/navigation";
import { getLocale, isLocale, localeCodes, locales } from "../i18n/config";
import { fontClassName } from "../i18n/fonts";
import { getDictionary } from "../i18n/dictionaries";
import "../globals.css";

export function generateStaticParams() {
  return localeCodes.map((locale) => ({ locale }));
}

/**
 * Absolute URLs for og:image and friends, resolved per host so a preview
 * deployment never advertises another origin's assets.
 */
const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL ??
  (process.env.VERCEL_PROJECT_PRODUCTION_URL
    ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`
    : "https://computer-architecture-lab.openai.site");

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) return {};
  const config = getLocale(locale);
  const { ui } = await getDictionary(locale);
  const image = { url: "/og.jpg", width: 1200, height: 675, alt: ui.meta.imageAlt };

  return {
    metadataBase: new URL(siteUrl),
    title: ui.meta.title,
    description: ui.meta.description,
    applicationName: "Computer Architecture Lab",
    // Reinforces the `translate="no"` opt-out for tools that only read meta tags
    // (Google Translate and several translation extensions).
    other: { google: "notranslate" },
    alternates: {
      canonical: `/${locale}`,
      // Lets search engines serve the right language and offer the rest.
      languages: {
        ...Object.fromEntries(locales.map((entry) => [entry.code, `/${entry.code}`])),
        "x-default": "/zh",
      },
    },
    icons: {
      icon: [
        { url: "/favicon.svg", type: "image/svg+xml" },
        { url: "/icon-192.png", sizes: "192x192", type: "image/png" },
        { url: "/icon-512.png", sizes: "512x512", type: "image/png" },
      ],
      shortcut: "/favicon.svg",
      apple: { url: "/apple-touch-icon.png", sizes: "180x180" },
    },
    openGraph: {
      type: "website",
      siteName: "Computer Architecture Lab",
      locale: config.intl,
      alternateLocale: locales.filter((entry) => entry.code !== locale).map((entry) => entry.intl),
      title: ui.meta.ogTitle,
      description: ui.meta.ogDescription,
      images: [image],
    },
    twitter: {
      card: "summary_large_image",
      title: ui.meta.ogTitle,
      description: ui.meta.ogDescription,
      images: [image],
    },
  };
}

export const viewport: Viewport = { themeColor: "#071014" };

export default async function LocaleLayout({
  children,
  params,
}: Readonly<{ children: React.ReactNode; params: Promise<{ locale: string }> }>) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  const config = getLocale(locale);

  return (
    // `translate="no"` opts the page out of external translation tools. The app
    // ships its own EN/ZH localisation, so a translation extension (e.g.
    // Immersive Translate) has nothing to do here — and letting it rewrite the
    // DOM (wrapping text in <font> tags) is exactly what breaks React hydration.
    // `suppressHydrationWarning` additionally tolerates any attribute a browser
    // extension injects onto <html> (e.g. a translate theme marker).
    <html lang={config.code} dir={config.dir} translate="no" suppressHydrationWarning>
      <body className={fontClassName(config.script)}>{children}</body>
    </html>
  );
}
