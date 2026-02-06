import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import SubscriberDetail from './pages/SubscriberDetail';

function App() {
    return (
        <BrowserRouter>
            <div className="app">
                <Navbar />
                <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/subscriber/:id" element={<SubscriberDetail />} />
                </Routes>
            </div>
        </BrowserRouter>
    );
}

export default App;
