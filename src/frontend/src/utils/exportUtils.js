import jsPDF from 'jspdf';
import 'jspdf-autotable';
import * as XLSX from 'xlsx';

/**
 * Dashboard PDF Export
 * Detaylı rapor oluşturur
 */
export const exportDashboardToPDF = (data, counts) => {
    const doc = new jsPDF();
    const timestamp = new Date().toLocaleString('tr-TR');

    // Header
    doc.setFontSize(18);
    doc.setTextColor(40);
    doc.text('NetPulse NOC Raporu', 14, 22);

    doc.setFontSize(10);
    doc.setTextColor(100);
    doc.text(`Oluşturulma Tarihi: ${timestamp}`, 14, 30);

    // Summary Stats
    doc.setFontSize(14);
    doc.setTextColor(40);
    doc.text('Özet İstatistikler', 14, 45);

    const totalCount = counts.GREEN + counts.YELLOW + counts.RED;

    doc.autoTable({
        startY: 50,
        head: [['Kategori', 'Adet', 'Yüzde']],
        body: [
            ['🟢 Sağlıklı', counts.GREEN, `${((counts.GREEN / totalCount) * 100).toFixed(1)}%`],
            ['🟡 Riskli', counts.YELLOW, `${((counts.YELLOW / totalCount) * 100).toFixed(1)}%`],
            ['🔴 Arızalı', counts.RED, `${((counts.RED / totalCount) * 100).toFixed(1)}%`],
            ['📊 TOPLAM', totalCount, '100%']
        ],
        theme: 'grid',
        headStyles: { fillColor: [99, 102, 241] },
        styles: { fontSize: 10 }
    });

    // Critical Subscribers (RED)
    if (data.lists.RED && data.lists.RED.length > 0) {
        doc.setFontSize(14);
        doc.text('Kritik Arızalı Aboneler', 14, doc.lastAutoTable.finalY + 15);

        const redData = data.lists.RED.slice(0, 20).map(sub => [
            `#${sub.id}`,
            sub.name,
            sub.region,
            sub.plan,
            sub.issue || 'Bağlantı Kopuk'
        ]);

        doc.autoTable({
            startY: doc.lastAutoTable.finalY + 20,
            head: [['Abone No', 'Ad Soyad', 'Bölge', 'Paket', 'Durum']],
            body: redData,
            theme: 'striped',
            headStyles: { fillColor: [220, 38, 38] },
            styles: { fontSize: 9 }
        });
    }

    // Warning Subscribers (YELLOW)
    if (data.lists.YELLOW && data.lists.YELLOW.length > 0) {
        doc.addPage();
        doc.setFontSize(14);
        doc.text('Performans Uyarısı Alan Aboneler', 14, 20);

        const yellowData = data.lists.YELLOW.slice(0, 30).map(sub => [
            `#${sub.id}`,
            sub.name,
            sub.region,
            sub.plan,
            sub.issue || 'Yüksek Ping'
        ]);

        doc.autoTable({
            startY: 25,
            head: [['Abone No', 'Ad Soyad', 'Bölge', 'Paket', 'Durum']],
            body: yellowData,
            theme: 'striped',
            headStyles: { fillColor: [251, 146, 60] },
            styles: { fontSize: 9 }
        });
    }

    // Footer
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(150);
        doc.text(
            `NetPulse NOC - Sayfa ${i} / ${pageCount}`,
            doc.internal.pageSize.width / 2,
            doc.internal.pageSize.height - 10,
            { align: 'center' }
        );
    }

    // Save
    doc.save(`NetPulse_Rapor_${new Date().toISOString().split('T')[0]}.pdf`);
};

/**
 * Liste Excel Export
 * Abone listesini Excel'e aktarır
 */
export const exportListToExcel = (subscribers, filterName) => {
    // Prepare data
    const excelData = subscribers.map(sub => ({
        'Abone No': `#${sub.id}`,
        'Ad Soyad': sub.name,
        'Bölge': sub.region,
        'Paket': sub.plan,
        'Durum': sub.status === 'GREEN' ? 'Sağlıklı' : sub.status === 'YELLOW' ? 'Riskli' : 'Arızalı',
        'Sorun': sub.issue || '-'
    }));

    // Create worksheet
    const ws = XLSX.utils.json_to_sheet(excelData);

    // Set column widths
    ws['!cols'] = [
        { wch: 12 },  // Abone No
        { wch: 25 },  // Ad Soyad
        { wch: 20 },  // Bölge
        { wch: 25 },  // Paket
        { wch: 12 },  // Durum
        { wch: 20 }   // Sorun
    ];

    // Create workbook
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Aboneler');

    // Save
    const fileName = `NetPulse_${filterName}_${new Date().toISOString().split('T')[0]}.xlsx`;
    XLSX.writeFile(wb, fileName);
};
