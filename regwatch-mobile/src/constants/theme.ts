export const theme = {
  bg: '#1a1a2e',
  surface: '#1e1e35',
  surfaceAlt: '#151525',
  hover: 'rgba(255, 255, 255, 0.04)',
  active: 'rgba(129, 140, 248, 0.12)',
  border: 'rgba(255, 255, 255, 0.06)',
  borderActive: 'rgba(129, 140, 248, 0.4)',

  textPrimary: '#e8e8f0',
  textSecondary: '#8888a8',
  textTertiary: '#5a5a78',

  accent: '#818cf8',
  accentMuted: 'rgba(129, 140, 248, 0.15)',

  impactHigh: '#f87171',
  impactHighBg: 'rgba(248, 113, 113, 0.12)',
  impactMedium: '#fbbf24',
  impactMediumBg: 'rgba(251, 191, 36, 0.12)',
  impactLow: '#34d399',
  impactLowBg: 'rgba(52, 211, 153, 0.12)',
  impactUnknown: '#64748b',
};

export function getImpactColor(impact: string): string {
  switch (impact) {
    case 'High': return theme.impactHigh;
    case 'Medium': return theme.impactMedium;
    case 'Low': return theme.impactLow;
    default: return theme.impactUnknown;
  }
}

export function getImpactBgColor(impact: string): string {
  switch (impact) {
    case 'High': return theme.impactHighBg;
    case 'Medium': return theme.impactMediumBg;
    case 'Low': return theme.impactLowBg;
    default: return 'rgba(100, 116, 139, 0.12)';
  }
}

export function timeAgo(dateStr: string): string {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const now = new Date();
  const diff = Math.floor((now.getTime() - d.getTime()) / 1000);
  if (diff < 60) return 'just now';
  if (diff < 3600) return Math.floor(diff / 60) + 'm';
  if (diff < 86400) return Math.floor(diff / 3600) + 'h';
  if (diff < 604800) return Math.floor(diff / 86400) + 'd';
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
}
