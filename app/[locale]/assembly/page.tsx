import { notFound } from "next/navigation";
import { AssemblyApp } from "../../components/AssemblyApp";
import { isLocale } from "../../i18n/config";

export default async function AssemblyPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  return <AssemblyApp locale={locale} />;
}
