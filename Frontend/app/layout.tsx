import './globals.css';
import { AuthProvider } from '../contexts/AuthContext';

export const metadata = {
  title: 'Sheily AI - Sistema de Inteligencia Artificial',
  description: 'Plataforma avanzada con 35 ramas especializadas de IA',
  keywords: 'IA, inteligencia artificial, machine learning, chat AI, Llama',
  authors: [{ name: 'Sheily AI Team' }],
  viewport: 'width=device-width, initial-scale=1',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-['Inter']">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
