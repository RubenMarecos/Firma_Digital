export default function(component) {
  const { parentElement, data, setStateValue } = component;
  const canvas = parentElement.querySelector('canvas');
  const hint = parentElement.querySelector('.hint');
  const status = parentElement.querySelector('.status');
  const clear = parentElement.querySelector('button');
  const ctx = canvas.getContext('2d');
  // Keep the bitmap on rerenders; restore it if Streamlit remounts the DOM.
  const model = canvas.signatureModel || { pointer: null, ink: false, revision: 0 };
  canvas.signatureModel = model;
  let disposed = false;
  function display() {
    hint.hidden = model.ink;
    status.textContent = model.ink ? 'Firma lista.' : 'Usá el mouse, el touchpad o tu dedo.';
  }
  if (!model.ink && data?.initial) {
    const revision = model.revision;
    const image = new Image();
    image.onload = () => {
      if (disposed || model.revision !== revision) return;
      ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
      model.ink = true;
      display();
    };
    image.src = data.initial;
  }
  display();
  function point(event) {
    const rect = canvas.getBoundingClientRect();
    return [(event.clientX - rect.left) * canvas.width / rect.width,
            (event.clientY - rect.top) * canvas.height / rect.height];
  }
  function start(event) {
    if (model.pointer !== null || !event.isPrimary || (event.pointerType === 'mouse' && event.button !== 0)) return;
    event.preventDefault();
    model.revision++;
    model.pointer = event.pointerId;
    canvas.setPointerCapture(event.pointerId);
    ctx.strokeStyle = '#173b69';
    ctx.fillStyle = '#173b69';
    ctx.lineWidth = 5;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    const [x, y] = point(event);
    ctx.beginPath();
    ctx.arc(x, y, 2.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(x, y);
    model.ink = true;
    hint.hidden = true;
    status.textContent = 'Dibujando…';
  }
  function move(event) {
    if (model.pointer !== event.pointerId) return;
    event.preventDefault();
    const events = event.getCoalescedEvents?.() || [];
    for (const sample of events.length ? events : [event]) {
      const [x, y] = point(sample);
      ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(...point(event));
  }
  function finish(event) {
    if (model.pointer !== event.pointerId) return;
    model.pointer = null;
    if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId);
    display();
    setStateValue('signature', canvas.toDataURL('image/png'));
  }
  function erase() {
    model.revision++;
    model.pointer = null;
    model.ink = false;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    display();
    setStateValue('signature', null);
  }
  canvas.addEventListener('pointerdown', start);
  canvas.addEventListener('pointermove', move);
  canvas.addEventListener('pointerup', finish);
  canvas.addEventListener('pointercancel', finish);
  canvas.addEventListener('lostpointercapture', finish);
  clear.addEventListener('click', erase);
  return () => {
    disposed = true;
    canvas.removeEventListener('pointerdown', start);
    canvas.removeEventListener('pointermove', move);
    canvas.removeEventListener('pointerup', finish);
    canvas.removeEventListener('pointercancel', finish);
    canvas.removeEventListener('lostpointercapture', finish);
    clear.removeEventListener('click', erase);
  };
}
