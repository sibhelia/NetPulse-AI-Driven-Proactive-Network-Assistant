# NetPulse - LSTM Cache Builder
# 12 kez istek atarak LSTM cache'ini doldurur

Write-Host "🚀 LSTM Cache Builder Başlatılıyor..." -ForegroundColor Cyan
Write-Host "Hedef: 12 ölçüm topla (LSTM için)" -ForegroundColor Yellow
Write-Host ""

$subscriberId = 1001
$apiUrl = "http://localhost:8000/api/simulate/$subscriberId"

for ($i = 1; $i -le 12; $i++) {
    Write-Host "[$i/12] Ölçüm alınıyor..." -NoNewline
    
    try {
        $response = Invoke-RestMethod -Uri $apiUrl -Method Get -UseBasicParsing
        
        if ($response.ai_analysis.trend.available) {
            Write-Host " ✅ LSTM AKTİF!" -ForegroundColor Green
        } else {
            $cached = $response.ai_analysis.trend.measurements_cached
            Write-Host " Bekleniyor ($cached/12)" -ForegroundColor Gray
        }
    }
    catch {
        Write-Host " ❌ Hata" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "✅ Tamamlandı! LSTM şimdi aktif olmalı." -ForegroundColor Green
Write-Host "Frontend'de detay sayfasını aç: http://localhost:3000/subscriber/1001" -ForegroundColor Cyan
