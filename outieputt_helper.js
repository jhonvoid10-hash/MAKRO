/**
 * ============================================================
 *  OutiePutt Auto-Play Helper Script
 *  Game: https://app.outieputt.com/ (Golf Billiard)
 * 
 *  CARA PAKAI:
 *  1. Buka game di Chrome Android
 *  2. Buka DevTools via chrome://inspect atau ADB:
 *     adb shell "am start -a android.intent.action.VIEW -d 'about:blank'"
 *  3. Paste script ini ke Console
 *  4. Ketik: OutiePuttBot.start()
 * 
 *  ATAU inject via MacroDroid → Action → JavaScript Interface
 * ============================================================
 */

const OutiePuttBot = (() => {
  
  // ============================================================
  //  KONFIGURASI — Sesuaikan dengan tampilan game
  // ============================================================
  const CONFIG = {
    // Delay antar aksi (ms)
    SHOT_DELAY: 2500,       // Tunggu bola berhenti
    HOLE_TRANSITION: 1500,  // Tunggu transisi hole
    INIT_DELAY: 2000,       // Tunggu game load
    
    // Kekuatan tembakan (0.0 - 1.0)
    POWER_NEAR: 0.3,        // Hole dekat
    POWER_MID: 0.55,        // Hole sedang
    POWER_FAR: 0.8,         // Hole jauh
    
    // Jumlah holes dalam satu game
    TOTAL_HOLES: 9,
    
    // Selector elemen game (sesuaikan jika game update)
    SELECTORS: {
      canvas: 'canvas',
      nextBtn: '[data-action="next"], .next-hole, .btn-next, #nextHole',
      playBtn: '[data-action="play"], .play-btn, #playButton, .start-game',
      scoreBoard: '.scoreboard, .score-display, #score'
    }
  };

  // ============================================================
  //  STATE
  // ============================================================
  let state = {
    currentHole: 0,
    totalShots: 0,
    scores: [],
    running: false,
    canvas: null,
    ctx: null
  };

  // ============================================================
  //  UTILITY FUNCTIONS
  // ============================================================
  
  const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  const log = (msg) => {
    const time = new Date().toLocaleTimeString('id-ID');
    console.log(`%c[OutiePuttBot ${time}] ${msg}`, 'color: #4CAF50; font-weight: bold;');
  };

  const randomOffset = (value, range = 5) => {
    return value + (Math.random() * range * 2 - range);
  };

  // ============================================================
  //  SIMULASI INPUT (Touch Events)
  // ============================================================

  /**
   * Simulasi touch tap pada koordinat (x, y)
   */
  const simulateTap = (x, y, element = document) => {
    const events = ['touchstart', 'touchend', 'click'];
    events.forEach((eventType, i) => {
      setTimeout(() => {
        const touch = new Touch({
          identifier: Date.now() + i,
          target: element,
          clientX: x,
          clientY: y,
          screenX: x,
          screenY: y,
          pageX: x,
          pageY: y,
          radiusX: 5,
          radiusY: 5,
          rotationAngle: 0,
          force: 1
        });
        const event = new TouchEvent(eventType, {
          bubbles: true,
          cancelable: true,
          touches: eventType === 'touchend' ? [] : [touch],
          targetTouches: eventType === 'touchend' ? [] : [touch],
          changedTouches: [touch]
        });
        element.dispatchEvent(event);
      }, i * 50);
    });
  };

  /**
   * Simulasi swipe dari (x1,y1) ke (x2,y2)
   * Ini adalah cara main OutiePutt: drag untuk aim & set power
   */
  const simulateSwipe = async (x1, y1, x2, y2, durationMs = 300) => {
    const steps = 20;
    const stepDelay = durationMs / steps;
    
    // Touch Start
    const startTouch = new Touch({
      identifier: Date.now(),
      target: document.body,
      clientX: x1, clientY: y1,
      screenX: x1, screenY: y1,
      pageX: x1, pageY: y1,
      radiusX: 5, radiusY: 5,
      rotationAngle: 0, force: 1
    });
    
    document.body.dispatchEvent(new TouchEvent('touchstart', {
      bubbles: true, cancelable: true,
      touches: [startTouch],
      targetTouches: [startTouch],
      changedTouches: [startTouch]
    }));

    // Touch Move (simulasi drag)
    for (let i = 1; i <= steps; i++) {
      await sleep(stepDelay);
      const progress = i / steps;
      const currentX = x1 + (x2 - x1) * progress;
      const currentY = y1 + (y2 - y1) * progress;
      
      const moveTouch = new Touch({
        identifier: Date.now(),
        target: document.body,
        clientX: currentX, clientY: currentY,
        screenX: currentX, screenY: currentY,
        pageX: currentX, pageY: currentY,
        radiusX: 5, radiusY: 5,
        rotationAngle: 0, force: 1
      });
      
      document.body.dispatchEvent(new TouchEvent('touchmove', {
        bubbles: true, cancelable: true,
        touches: [moveTouch],
        targetTouches: [moveTouch],
        changedTouches: [moveTouch]
      }));
    }

    // Touch End
    const endTouch = new Touch({
      identifier: Date.now(),
      target: document.body,
      clientX: x2, clientY: y2,
      screenX: x2, screenY: y2,
      pageX: x2, pageY: y2,
      radiusX: 5, radiusY: 5,
      rotationAngle: 0, force: 1
    });
    
    document.body.dispatchEvent(new TouchEvent('touchend', {
      bubbles: true, cancelable: true,
      touches: [],
      targetTouches: [],
      changedTouches: [endTouch]
    }));
    
    log(`Swipe: (${Math.round(x1)},${Math.round(y1)}) → (${Math.round(x2)},${Math.round(y2)})`);
  };

  // ============================================================
  //  GAME LOGIC
  // ============================================================

  /**
   * Hitung posisi drag berdasarkan posisi bola dan target hole
   * Di game biliar: kamu drag ke arah BERLAWANAN dari target
   * (seperti menarik stik ke belakang)
   */
  const calculateShot = (ballX, ballY, holeX, holeY) => {
    const dx = holeX - ballX;
    const dy = holeY - ballY;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const angle = Math.atan2(dy, dx);
    
    // Tentukan power berdasarkan jarak
    const screenDiag = Math.sqrt(window.innerWidth ** 2 + window.innerHeight ** 2);
    const distRatio = distance / screenDiag;
    
    let power;
    if (distRatio < 0.2) power = CONFIG.POWER_NEAR;
    else if (distRatio < 0.4) power = CONFIG.POWER_MID;
    else power = CONFIG.POWER_FAR;
    
    // Drag ke arah berlawanan (backswing)
    const dragDist = power * 200; // pixel
    const dragX = ballX - Math.cos(angle) * dragDist;
    const dragY = ballY - Math.sin(angle) * dragDist;
    
    return {
      startX: ballX,
      startY: ballY,
      endX: dragX,
      endY: dragY,
      power: power,
      angle: (angle * 180 / Math.PI).toFixed(1),
      distance: distance.toFixed(0)
    };
  };

  /**
   * Posisi hole untuk tiap nomor (estimasi berdasarkan layout game)
   * Koordinat dalam pixel untuk layar 1080x2400
   * Sesuaikan dengan layar kamu!
   */
  const getHolePosition = (holeNumber) => {
    const W = window.innerWidth;
    const H = window.innerHeight;
    
    // Layout estimasi 9 holes OutiePutt
    const holes = {
      1: { x: W * 0.20, y: H * 0.15 },  // Kiri atas
      2: { x: W * 0.80, y: H * 0.15 },  // Kanan atas
      3: { x: W * 0.50, y: H * 0.20 },  // Tengah atas
      4: { x: W * 0.15, y: H * 0.45 },  // Kiri tengah
      5: { x: W * 0.85, y: H * 0.45 },  // Kanan tengah
      6: { x: W * 0.50, y: H * 0.40 },  // Tengah
      7: { x: W * 0.25, y: H * 0.70 },  // Kiri bawah
      8: { x: W * 0.75, y: H * 0.70 },  // Kanan bawah
      9: { x: W * 0.50, y: H * 0.65 },  // Tengah bawah
    };
    
    return holes[holeNumber] || { x: W * 0.5, y: H * 0.3 };
  };

  /**
   * Posisi bola putih (estimasi — di tengah-bawah layar)
   */
  const getBallPosition = () => {
    return {
      x: window.innerWidth * 0.50,
      y: window.innerHeight * 0.58
    };
  };

  /**
   * Cari dan klik tombol "Next Hole" atau "Play Again"
   */
  const clickNextButton = async () => {
    // Coba selector yang umum
    const selectors = [
      'button[class*="next"]',
      'button[class*="Next"]', 
      'div[class*="next"]',
      '[data-action="next"]',
      'button:contains("Next")',
      '.next-hole',
      '#nextHole',
      'button'  // fallback: klik semua tombol
    ];
    
    for (const sel of selectors) {
      try {
        const el = document.querySelector(sel);
        if (el && el.offsetParent !== null) { // visible
          el.click();
          log(`✅ Klik tombol: ${sel}`);
          return true;
        }
      } catch(e) {}
    }
    
    // Fallback: tap koordinat tombol "Next" (biasanya di bawah tengah)
    const x = window.innerWidth * 0.5;
    const y = window.innerHeight * 0.8;
    log(`⚠️ Tombol tidak ditemukan, tap koordinat fallback (${x}, ${y})`);
    simulateTap(x, y);
    return false;
  };

  /**
   * Main satu hole
   */
  const playHole = async (holeNum) => {
    log(`\n⛳ ===== HOLE ${holeNum} =====`);
    
    const ball = getBallPosition();
    const hole = getHolePosition(holeNum);
    
    log(`📍 Bola: (${ball.x.toFixed(0)}, ${ball.y.toFixed(0)})`);
    log(`🕳️ Hole: (${hole.x.toFixed(0)}, ${hole.y.toFixed(0)})`);
    
    let shotCount = 0;
    const maxShots = 5; // Maksimal 5 tembakan per hole
    
    while (shotCount < maxShots) {
      shotCount++;
      state.totalShots++;
      
      const shot = calculateShot(
        randomOffset(ball.x, 3),
        randomOffset(ball.y, 3),
        hole.x,
        hole.y
      );
      
      log(`🎱 Tembakan #${shotCount} | Power: ${(shot.power * 100).toFixed(0)}% | Sudut: ${shot.angle}° | Jarak: ${shot.distance}px`);
      
      await simulateSwipe(
        shot.startX, shot.startY,
        shot.endX, shot.endY,
        350
      );
      
      await sleep(CONFIG.SHOT_DELAY);
      
      // Cek apakah sudah ada tombol "Next Hole" (berarti bola masuk)
      const nextBtn = document.querySelector(
        'button[class*="next"], .next-hole, [data-action="next"], button'
      );
      
      if (nextBtn && nextBtn.offsetParent !== null) {
        log(`✅ HOLE ${holeNum} SELESAI dalam ${shotCount} tembakan!`);
        state.scores.push(shotCount);
        break;
      }
      
      if (shotCount < maxShots) {
        log(`↩️ Bola belum masuk, tembak lagi...`);
        await sleep(500);
      }
    }
    
    if (shotCount >= maxShots) {
      log(`⚠️ Maks tembakan tercapai untuk hole ${holeNum}`);
      state.scores.push(shotCount);
    }
  };

  // ============================================================
  //  MAIN CONTROLLER
  // ============================================================

  const start = async () => {
    if (state.running) {
      log('⚠️ Bot sudah berjalan!');
      return;
    }
    
    state.running = true;
    state.currentHole = 0;
    state.totalShots = 0;
    state.scores = [];
    
    log('🚀 OutiePutt Bot DIMULAI!');
    log(`📱 Layar: ${window.innerWidth} x ${window.innerHeight}`);
    
    // Klik tombol START/PLAY
    await sleep(CONFIG.INIT_DELAY);
    const startBtn = document.querySelector(
      '[data-action="play"], .play-btn, #playButton, .start-game, button'
    );
    if (startBtn) {
      startBtn.click();
      log('▶️ Klik tombol START');
    } else {
      simulateTap(window.innerWidth * 0.5, window.innerHeight * 0.75);
      log('▶️ Tap layar untuk START');
    }
    await sleep(2000);
    
    // Loop tiap hole
    for (let hole = 1; hole <= CONFIG.TOTAL_HOLES; hole++) {
      state.currentHole = hole;
      await playHole(hole);
      await sleep(CONFIG.HOLE_TRANSITION);
      await clickNextButton();
      await sleep(CONFIG.HOLE_TRANSITION);
    }
    
    // Selesai!
    const totalScore = state.scores.reduce((a, b) => a + b, 0);
    const avgScore = (totalScore / CONFIG.TOTAL_HOLES).toFixed(1);
    
    log('\n🏆 ===== GAME SELESAI! =====');
    log(`📊 Skor tiap hole: [${state.scores.join(', ')}]`);
    log(`🎯 Total tembakan: ${state.totalShots}`);
    log(`📈 Rata-rata per hole: ${avgScore}`);
    
    // Tampilkan overlay skor
    showScoreOverlay(state.scores, totalScore);
    
    state.running = false;
  };

  const stop = () => {
    state.running = false;
    log('⏹️ Bot dihentikan.');
  };

  /**
   * Tampilkan overlay skor di layar
   */
  const showScoreOverlay = (scores, total) => {
    const existing = document.getElementById('outieputt-bot-overlay');
    if (existing) existing.remove();
    
    const overlay = document.createElement('div');
    overlay.id = 'outieputt-bot-overlay';
    overlay.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: rgba(0,0,0,0.92);
      color: white;
      padding: 24px 32px;
      border-radius: 16px;
      z-index: 99999;
      font-family: Arial, sans-serif;
      font-size: 15px;
      min-width: 280px;
      text-align: center;
      border: 2px solid #4CAF50;
    `;
    
    const rows = scores.map((s, i) => 
      `<tr>
        <td style="padding:4px 12px">Hole ${i+1}</td>
        <td style="padding:4px 12px; color:${s <= 2 ? '#4CAF50' : s <= 4 ? '#FFC107' : '#f44336'}">
          ${s} tembakan ${s === 1 ? '🎉' : s <= 2 ? '✅' : ''}
        </td>
      </tr>`
    ).join('');
    
    overlay.innerHTML = `
      <div style="font-size:24px;margin-bottom:12px">🏆 Game Selesai!</div>
      <table style="width:100%;margin-bottom:12px">${rows}</table>
      <div style="border-top:1px solid #555;padding-top:12px;font-size:18px">
        Total: <strong>${total} tembakan</strong>
      </div>
      <button onclick="document.getElementById('outieputt-bot-overlay').remove()"
        style="margin-top:14px;padding:8px 20px;background:#4CAF50;color:white;border:none;border-radius:8px;cursor:pointer;font-size:14px">
        Tutup
      </button>
    `;
    
    document.body.appendChild(overlay);
  };

  // ============================================================
  //  PUBLIC API
  // ============================================================
  return {
    start,
    stop,
    config: CONFIG,
    state,
    // Utilitas untuk kalibrasi manual
    testTap: (x, y) => simulateTap(x, y),
    testSwipe: (x1, y1, x2, y2) => simulateSwipe(x1, y1, x2, y2),
    showInfo: () => {
      log(`Layar: ${window.innerWidth}x${window.innerHeight}`);
      log(`Running: ${state.running}`);
      log(`Hole: ${state.currentHole}`);
      log(`Scores: [${state.scores.join(', ')}]`);
    }
  };

})();

// Auto-run info saat script diload
console.log('%c🏌️ OutiePutt Bot Loaded!', 'font-size:16px; color:#4CAF50; font-weight:bold;');
console.log('%cPerintah:', 'font-weight:bold;');
console.log('  OutiePuttBot.start()     → Mulai bot');
console.log('  OutiePuttBot.stop()      → Hentikan bot');
console.log('  OutiePuttBot.showInfo()  → Lihat status');
console.log('  OutiePuttBot.testTap(x, y)           → Test tap koordinat');
console.log('  OutiePuttBot.testSwipe(x1,y1, x2,y2) → Test swipe');
