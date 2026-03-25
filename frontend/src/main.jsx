import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import { store } from './store'
import "mango-ui-kit/dist/mango-ui-kit.css";
import './index.css'
import App from './App.jsx'
import { ThemeProvider } from 'mango-ui-kit'
import { myTheme } from './configs/theme.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <ThemeProvider theme={myTheme} defaultThemeMode="light">
          <App />
        </ThemeProvider>
      </BrowserRouter>
    </Provider>
  </StrictMode>
)


