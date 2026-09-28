import './globals.css';

export const metadata = { title: 'TaskFlow', description: 'Hairdrama Tech task management assignment' };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
