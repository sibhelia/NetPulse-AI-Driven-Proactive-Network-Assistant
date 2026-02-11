const API_BASE = 'http://localhost:8000';

export const api = {
    // Ana dashboard verisi - Tüm aboneler
    getAllSubscribers: async () => {
        try {
            const res = await fetch(`${API_BASE}/api/scan_network`);
            if (!res.ok) throw new Error('Network response was not ok');
            return await res.json();
        } catch (error) {
            console.error('Error fetching subscribers:', error);
            throw error;
        }
    },

    // Tekil abone detayı (RF + LSTM hybrid)
    getSubscriberDetail: async (subscriberId) => {
        try {
            const res = await fetch(`${API_BASE}/api/simulate/${subscriberId}`);
            if (!res.ok) throw new Error('Subscriber not found');
            return await res.json();
        } catch (error) {
            console.error(`Error fetching subscriber ${subscriberId}:`, error);
            throw error;
        }
    },

    // LSTM trend analizi
    getTrendAnalysis: async (subscriberId) => {
        try {
            const res = await fetch(`${API_BASE}/api/trend/${subscriberId}`);
            if (!res.ok) {
                // 400 = Not enough data, gracefully handle
                if (res.status === 400) {
                    return { error: 'not_enough_data', message: 'Trend analizi için en az 1 saatlik veri gerekli' };
                }
                throw new Error('Trend analysis failed');
            }
            return await res.json();
        } catch (error) {
            console.error(`Error fetching trend for ${subscriberId}:`, error);
            throw error;
        }
    },

    // --- NEW METHODS (Action & Ticketing) ---
    getTechnicians: async () => {
        const res = await fetch(`${API_BASE}/api/technicians`);
        return await res.json();
    },

    createTicket: async (ticketData) => {
        const res = await fetch(`${API_BASE}/api/tickets`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(ticketData)
        });
        if (!res.ok) {
            const errorData = await res.json();
            console.error('❌ Backend error:', JSON.stringify(errorData, null, 2));
            throw new Error(JSON.stringify(errorData.detail || errorData));
        }
        return await res.json();
    },

    performAction: async (actionType, subscriberId) => {
        const res = await fetch(`${API_BASE}/api/actions/${actionType}?subscriber_id=${subscriberId}`, {
            method: 'POST'
        });
        return await res.json();
    },

    // --- NEW: Smart Ticket Note Generation ---
    generateTicketNote: async (data) => {
        const res = await fetch(`${API_BASE}/api/generate_ticket_note`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error('Note generation failed');
        return await res.json();
    },

    // --- Ticket Management ---
    getSubscriberTickets: async (subscriberId) => {
        const res = await fetch(`${API_BASE}/api/tickets/${subscriberId}`);
        if (!res.ok) throw new Error('Failed to fetch tickets');
        return await res.json();
    },

    getAllTickets: async (status = null) => {
        const url = status
            ? `${API_BASE}/api/tickets?status=${status}`
            : `${API_BASE}/api/tickets`;
        const res = await fetch(url);
        if (!res.ok) throw new Error('Failed to fetch tickets');
        return await res.json();
    },

    updateTicketStatus: async (ticketId, statusData) => {
        const res = await fetch(`${API_BASE}/api/tickets/${ticketId}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(statusData)
        });
        if (!res.ok) throw new Error('Failed to update ticket status');
        return await res.json();
    },

    addTechnicianNote: async (ticketId, noteData) => {
        const res = await fetch(`${API_BASE}/api/tickets/${ticketId}/note`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(noteData)
        });
        if (!res.ok) throw new Error('Failed to add note');
        return await res.json();
    }
};
