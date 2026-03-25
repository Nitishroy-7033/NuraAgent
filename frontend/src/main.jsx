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
import { ThemeProvider as AppThemeProvider, useTheme } from './context/ThemeContext.jsx';

const Root = () => {
  const { theme } = useTheme();
  
  return (
    <ThemeProvider theme={myTheme} themeMode={theme}>
      <App />
    </ThemeProvider>
  );
};

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <AppThemeProvider>
          <Root />
        </AppThemeProvider>
      </BrowserRouter>
    </Provider>
  </StrictMode>
)


