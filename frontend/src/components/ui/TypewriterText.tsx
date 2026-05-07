'use client';
import { useState, useEffect, useRef } from 'react';

interface Props {
  text: string;
  speed?: number;
  onDone?: () => void;
  boldFirstSentence?: boolean;
}

function splitFirstSentence(text: string): [string, string] {
  const m = text.match(/^(.*?[.!?])\s/s);
  if (m) return [m[1], text.slice(m[0].length)];
  const nl = text.indexOf('\n');
  if (nl > 0) return [text.slice(0, nl), text.slice(nl + 1)];
  return [text, ''];
}

export function TypewriterText({ text, speed = 25, onDone, boldFirstSentence }: Props) {
  const [displayed, setDisplayed] = useState('');
  const indexRef = useRef(0);
  const onDoneRef = useRef(onDone);
  onDoneRef.current = onDone;

  useEffect(() => {
    indexRef.current = 0;
    setDisplayed('');

    const id = setInterval(() => {
      indexRef.current += 1;
      setDisplayed(text.slice(0, indexRef.current));
      if (indexRef.current >= text.length) {
        clearInterval(id);
        onDoneRef.current?.();
      }
    }, speed);

    return () => clearInterval(id);
  }, [text, speed]);

  if (boldFirstSentence) {
    const [first, rest] = splitFirstSentence(displayed);
    return <><strong>{first}</strong>{rest ? <><br />{rest}</> : null}</>;
  }
  return <>{displayed}</>;
}

export { splitFirstSentence };
