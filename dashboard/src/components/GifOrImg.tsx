import React from 'react';

export const GifOrImg: React.FC<{ src: string; alt: string; className?: string }> = ({ src, alt, className }) => {
  // If it's a gif, use <img> with no object-fit, else use normal styling
  const isGif = src.toLowerCase().endsWith('.gif');
  return (
    <img
      src={src}
      alt={alt}
      className={className + (isGif ? ' bg-black object-contain' : ' object-cover')}
      style={isGif ? { background: 'black', objectFit: 'contain' } : {}}
      loading="lazy"
    />
  );
};
