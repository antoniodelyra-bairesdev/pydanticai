import Script from "next/script";
import Navigation from "./_components/menu-lateral/Navigation";
import { ClientProviders } from "./clientProviders";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <head>
        <style>
          {`html {
            overflow: hidden;
          }
          .ag-watermark {
            visibility: hidden !important;
          }`}
        </style>
      </head>
      <body>
        <ClientProviders>
          <Navigation>{children}</Navigation>
        </ClientProviders>
        <Script>
          {`
          document.body.style.opacity = 1
          const today = new Date()
          const diaAlvo = 1
          const mesAlvo = 4
          const threshold = 0.325
          let nextFrame
          if (today.getDate() === diaAlvo && today.getMonth() + 1 === mesAlvo) {
            if (Math.random() < 0.25) {
              console.log('Deu branco.')
              brilha()
            }
          }
          function fix() {
            if (nextFrame !== undefined) {
              cancelAnimationFrame(nextFrame)
            }
            if (document.body.style.opacity != 1) {
              document.body.style.opacity = 1
              console.log('Fim do momento de clareza.')
            }
          }
          function brilha() {
            const op = Math.max(Number(document.body.style.opacity) - 0.0001, 0)
            document.body.style.opacity = op
            if (op > threshold) {
              nextFrame = requestAnimationFrame(brilha)
            } else {
              document.body.style.opacity = threshold
              console.log('O sistema é brilhante.')
            }
          }
          `}
        </Script>
      </body>
    </html>
  );
}
