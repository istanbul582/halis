import React from 'react';
import {
  AbsoluteFill,
  Easing,
  interpolate,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {loadFont} from '@remotion/fonts';

// Original artwork and animation. Reference clips are deliberately absent.
const fonts = Promise.all([
  loadFont({family: 'Manrope', url: staticFile('fonts/Manrope.ttf'), weight: '200 800'}),
  loadFont({family: 'Barlow Condensed', url: staticFile('fonts/BarlowCondensed-ExtraBold.ttf'), weight: '800'}),
  loadFont({family: 'DM Serif', url: staticFile('fonts/DMSerifDisplay-Italic.ttf'), style: 'italic'}),
]);
void fonts;

const NAVY = '#101B32';
const IVORY = '#F3EFE5';
const GOLD = '#D7B77A';
const ease = Easing.bezier(0.22, 1, 0.36, 1);
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const motion = (frame: number, from: number, to: number, a = 0, b = 1) =>
  interpolate(frame, [from, to], [a, b], {...clamp, easing: ease});

const captions = [
  {start: 0, end: 1.421, text: '“Yaklaşık 50 bin lira'},
  {start: 1.421, end: 2.86, text: 'sermayeyle başlayarak…”'},
  {start: 3.1, end: 5.077, text: 'GUMA’nın ilk videosunda açıklanan'},
  {start: 5.077, end: 6, text: 'bütçe planı bu.'},
  {start: 6.36, end: 7.325, text: 'Ama aynı videoda'},
  {start: 7.325, end: 8.7, text: 'başka bir sayı daha var:'},
  {start: 8.96, end: 9.76, text: '130 bin.'},
  {start: 10.1, end: 10.88, text: 'Para değil.'},
  {start: 11.08, end: 11.84, text: 'Takipçi.'},
  {start: 12.18, end: 13.62, text: 'Videoyu anlatan kurucu,'},
  {start: 13.62, end: 15.426, text: 'daha önce 130 bin takipçiye'},
  {start: 15.426, end: 16.68, text: 'ulaştığını söylüyor.'},
];

const Photo: React.FC<{
  src: string;
  frame: number;
  duration: number;
  focus?: string;
  dark?: number;
}> = ({src, frame, duration, focus = '50% 50%', dark = 0}) => (
  <AbsoluteFill style={{overflow: 'hidden', background: NAVY}}>
    <OffthreadVideo
      src={staticFile(src)}
      muted
      style={{
        width: '100%',
        height: '100%',
        objectFit: 'cover',
        objectPosition: focus,
        transform: `scale(${motion(frame, 0, duration, 1.085, 1.018)}) translateX(${motion(frame, 0, duration, -14, 9)}px)`,
        filter: `saturate(.78) contrast(1.05) brightness(${0.96 - dark})`,
      }}
    />
    <AbsoluteFill style={{background: 'linear-gradient(180deg,rgba(7,14,28,.68) 0%,rgba(7,14,28,.52) 24%,rgba(7,14,28,.04) 49%,rgba(16,27,50,.06) 60%,#101B32 86%)'}} />
  </AbsoluteFill>
);

const SmallLabel: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => (
  <div style={{fontFamily: 'Manrope', fontSize: 23, fontWeight: 700, letterSpacing: 2.8, textTransform: 'uppercase', ...style}}>{children}</div>
);

const PhotoStripe: React.FC<{src: string; frame: number; start: number; x: number; width: number; focus?: string}> = ({src, frame, start, x, width, focus = '50% 50%'}) => {
  const p = motion(frame, start, start + 21);
  return <div style={{position: 'absolute', left: x, top: 930, width, height: 380, overflow: 'hidden', opacity: p, transform: `translateY(${(1 - p) * 90}px)`, borderTop: `2px solid ${GOLD}`}}>
    <OffthreadVideo src={staticFile(src)} muted style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: focus, transform: `scale(${1.12 - p * .08})`, filter: 'saturate(.65) contrast(1.06)'}} />
    <AbsoluteFill style={{background: 'linear-gradient(0deg,rgba(16,27,50,.46),transparent 70%)'}} />
  </div>;
};

export const Pilot: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const roomStart = 3.1 * fps;
  const creatorStart = 8.7 * fps;
  const roomReveal = motion(frame, roomStart, roomStart + 23);
  const creatorReveal = motion(frame, creatorStart, creatorStart + 18);
  const labelReveal = motion(frame, 3.1 * fps, 3.1 * fps + 22);
  const firstNumberOut = motion(frame, 6.36 * fps, 6.36 * fps + 19);
  const numberIn = motion(frame, 8.96 * fps, 8.96 * fps + 19);
  const followersIn = motion(frame, 11.08 * fps, 11.08 * fps + 15);
  const proofIn = motion(frame, 12.18 * fps, 12.18 * fps + 24);
  const caption = captions.find((c) => t >= c.start && t < c.end);
  const stockIds = t < 3.1 ? '7677808' : t < 3.9 ? '7677808 · 15887137' : t < 8.7 ? '15887137' : t < 9.35 ? '15887137 · 7806870' : '7806870';
  const captionProgress = caption ? motion(frame, caption.start * fps, caption.start * fps + 6) : 0;

  return (
    <AbsoluteFill style={{background: NAVY, color: IVORY, fontFamily: 'Manrope', overflow: 'hidden'}}>
      <Sequence from={0} durationInFrames={Math.ceil(6.8 * fps)}>
        <Photo src="material.mp4" frame={frame} duration={6.8 * fps} dark={.04} />
      </Sequence>

      <Sequence from={Math.round(roomStart)} durationInFrames={Math.ceil(6.3 * fps)}>
        <AbsoluteFill style={{clipPath: `polygon(${(1 - roomReveal) * 145}% 0,100% 0,100% 100%,${(1 - roomReveal) * 145 - 23}% 100%)`}}>
          <Photo src="room.mp4" frame={frame - roomStart} duration={6.3 * fps} focus="50% 48%" dark={.08} />
        </AbsoluteFill>
      </Sequence>

      <Sequence from={Math.round(creatorStart)} durationInFrames={Math.ceil((17 - 8.7) * fps)}>
        <AbsoluteFill style={{clipPath: `polygon(0 ${(1 - creatorReveal) * 115}%,100% ${(1 - creatorReveal) * 115 - 12}%,100% 100%,0 100%)`}}>
          <Photo src="creator.mp4" frame={frame - creatorStart} duration={(17 - 8.7) * fps} focus="51% 53%" dark={.11} />
        </AbsoluteFill>
      </Sequence>

      {/* A quiet persistent editorial masthead, never a brand logo. */}
      <div style={{position: 'absolute', top: 110, left: 80, fontFamily: 'DM Serif', fontStyle: 'italic', fontSize: 34, letterSpacing: -.3}}>Bir markanın başlangıcı</div>
      <div style={{position: 'absolute', top: 120, right: 82, fontSize: 20, letterSpacing: 2.6, fontWeight: 600}}>GUMA</div>
      <svg width="1080" height="70" viewBox="0 0 1080 70" style={{position: 'absolute', top: 159, left: 0}}>
        <line x1="83" y1="20" x2="997" y2="20" stroke={IVORY} strokeOpacity=".23" strokeWidth="1" strokeDasharray="2 6" />
        <line x1="83" y1="20" x2={83 + 914 * motion(frame, 0, 510)} y2="20" stroke={GOLD} strokeWidth="2" />
        <circle cx={83 + 914 * motion(frame, 0, 510)} cy="20" r="5" fill={GOLD} />
      </svg>

      {/* The opening number moves with the camera; the full photo stays visible. */}
      <div style={{position: 'absolute', left: 80, top: 345 - labelReveal * 32 - firstNumberOut * 140, opacity: 1 - firstNumberOut, transform: `translateY(${motion(frame, 0, 17, 20, 0)}px)`}}>
        <div style={{fontFamily: 'DM Serif', fontStyle: 'italic', fontSize: 54, marginBottom: 3, color: GOLD, opacity: 1 - labelReveal}}>Yaklaşık</div>
        <div style={{display: 'flex', alignItems: 'baseline', gap: 22, lineHeight: .88, textShadow: '0 3px 30px rgba(0,0,0,.12)'}}>
          <span style={{fontFamily: 'Barlow Condensed', fontWeight: 800, fontSize: 282, letterSpacing: -4}}>50.000</span>
          <span style={{fontFamily: 'Manrope', fontWeight: 700, fontSize: 69, letterSpacing: -3}}>TL</span>
        </div>
        <div style={{marginTop: 28, opacity: labelReveal, transform: `translateY(${(1 - labelReveal) * 25}px)`}}>
          <SmallLabel style={{fontSize: 22, color: GOLD, marginBottom: 7}}>İlk videoda açıklanan</SmallLabel>
          <div style={{fontFamily: 'DM Serif', fontStyle: 'italic', fontSize: 67, lineHeight: 1}}>bütçe planı.</div>
        </div>
      </div>

      {/* The tease follows the narration rather than showing a fictitious counter. */}
      <div style={{position: 'absolute', left: 82, top: 260, opacity: firstNumberOut * (1 - numberIn), transform: `translateY(${(1 - firstNumberOut) * 24}px)`}}>
        <SmallLabel style={{fontSize: 20, color: GOLD, marginBottom: 17}}>Açıklanan bütçe planı</SmallLabel>
        <div style={{fontSize: 42, fontWeight: 700, letterSpacing: -1}}>50.000 TL</div>
      </div>
      <div style={{position: 'absolute', left: 82, top: 540, opacity: firstNumberOut * (1 - numberIn), transform: `translateY(${(1 - firstNumberOut) * 40}px)`}}>
        <div style={{fontWeight: 800, fontSize: 86, lineHeight: 1.05, letterSpacing: -4}}>Bir sayı</div>
        <div style={{fontFamily: 'DM Serif', fontStyle: 'italic', fontSize: 109, color: GOLD, lineHeight: 1.05}}>daha var.</div>
      </div>

      {/* An original line connects the two pieces of the story, not measured data. */}
      <svg viewBox="0 0 1080 1920" width="1080" height="1920" style={{position: 'absolute', left: 0, top: 0, opacity: motion(frame, 6.5 * fps, 7.05 * fps) * (1 - proofIn)}}>
        <path d="M 370 364 C 655 395 868 590 863 809 C 860 945 750 1037 550 1068" stroke={GOLD} strokeWidth="2.5" fill="none" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - motion(frame, 6.6 * fps, 8.7 * fps)} />
        <circle cx="370" cy="364" r="6" fill={GOLD} />
      </svg>

      <div style={{position: 'absolute', left: 77, top: 350 - proofIn * 22, opacity: numberIn, transform: `translateY(${(1 - numberIn) * 70}px) scale(${1 + (1 - numberIn) * .045})`, transformOrigin: 'left top'}}>
        <SmallLabel style={{fontSize: 22, color: GOLD, marginBottom: 19}}>Geçmiş takipçi sayısı beyanı</SmallLabel>
        <div style={{fontFamily: 'Barlow Condensed', fontSize: 291, lineHeight: .88, fontWeight: 800, letterSpacing: -4, textShadow: '0 4px 35px rgba(0,0,0,.25)'}}>130.000</div>
        <div style={{position: 'relative', height: 118, marginTop: 26}}>
          <div style={{position: 'absolute', left: 6, top: 0, fontFamily: 'DM Serif', fontSize: 71, fontStyle: 'italic', color: GOLD, opacity: followersIn, transform: `translateX(${(1 - followersIn) * 28}px)`}}>takipçi.</div>
          <div style={{position: 'absolute', left: 8, top: 85, fontSize: 22, fontWeight: 500, letterSpacing: .5, opacity: proofIn}}>Kurucunun geçmişte ulaştığını söylediği sayı</div>
        </div>
      </div>

      {/* Material → product → audience: real photographic detail, with no fake dashboard. */}
      <Sequence from={Math.round(12.65 * fps)} durationInFrames={Math.round(4.35 * fps)}>
        <PhotoStripe src="material.mp4" frame={frame} start={12.65 * fps} x={80} width={290} focus="50% 62%" />
      </Sequence>
      <Sequence from={Math.round(12.82 * fps)} durationInFrames={Math.round(4.18 * fps)}>
        <PhotoStripe src="room.mp4" frame={frame} start={12.82 * fps} x={382} width={290} focus="38% 62%" />
      </Sequence>
      <Sequence from={Math.round(12.99 * fps)} durationInFrames={Math.round(4.01 * fps)}>
        <PhotoStripe src="creator.mp4" frame={frame} start={12.99 * fps} x={684} width={290} focus="50% 50%" />
      </Sequence>
      <div style={{position: 'absolute', left: 81, top: 1330, fontSize: 20, opacity: proofIn * .85, letterSpacing: .6, color: '#C5C8D0'}}>Temsili görseller · malzeme / ürün / içerik üretimi</div>

      {/* Captions and provenance stay inside Instagram's useful area. */}
      <div style={{position: 'absolute', left: 72, right: 100, top: 1488, minHeight: 110, textAlign: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <div style={{fontSize: 43, fontWeight: 700, lineHeight: 1.3, letterSpacing: -1.1, opacity: captionProgress, transform: `translateY(${(1 - captionProgress) * 10}px)`, textShadow: '0 3px 15px rgba(0,0,0,.25)'}}>{caption?.text}</div>
      </div>
      <div style={{position: 'absolute', left: 80, right: 110, top: 1647, color: '#BAC0CB', fontSize: 19, textAlign: 'center', lineHeight: 1.6, fontWeight: 400}}>
        <div>Kaynak: youtube.com/shorts/nnUXsnz3Wi0 · 1. gün</div>
        <div style={{fontSize: 18, opacity: .78}}>{t >= 12.65 ? 'Temsili stok: Pexels / 7677808 · 15887137 · 7806870' : `Temsili stok: Pexels / ${stockIds}`}</div>
      </div>

      <div style={{position: 'absolute', left: 80, bottom: 88, color: '#828A9D', fontSize: 17, letterSpacing: 3}}>BAŞLANGIÇ KOŞULLARI</div>
      <div style={{position: 'absolute', right: 85, bottom: 85, color: GOLD, fontSize: 22, fontFamily: 'DM Serif', fontStyle: 'italic'}}>01</div>
    </AbsoluteFill>
  );
};
