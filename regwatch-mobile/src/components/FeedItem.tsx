import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { theme, getImpactColor, timeAgo } from '@/constants/theme';
import type { RegulatoryUpdate } from '@/constants/api';

interface FeedItemProps {
  item: RegulatoryUpdate;
  onPress: () => void;
  showScore?: boolean;
}

export default function FeedItem({ item, onPress, showScore }: FeedItemProps) {
  const impactColor = getImpactColor(item.regulatory_impact);
  const entities = (item.affected_entities || '')
    .split(',')
    .map(e => e.trim())
    .filter(e => e)
    .slice(0, 3);

  return (
    <Pressable
      style={({ pressed }) => [styles.container, pressed && styles.pressed]}
      onPress={onPress}
    >
      <View style={[styles.dot, { backgroundColor: impactColor }]} />
      <View style={styles.body}>
        <Text style={styles.title} numberOfLines={2}>{item.title}</Text>
        <View style={styles.meta}>
          <Text style={styles.source}>{item.source}</Text>
          <Text style={styles.time}>{timeAgo(item.publishedAt)}</Text>
          {entities.map((e, i) => (
            <View key={i} style={styles.tagContainer}>
              <Text style={styles.tag}>{e}</Text>
            </View>
          ))}
        </View>
      </View>
      {showScore && item.score !== undefined && (
        <View style={styles.scoreBadge}>
          <Text style={styles.scoreText}>{Math.round(item.score * 100)}%</Text>
        </View>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: theme.border,
    gap: 12,
  },
  pressed: {
    backgroundColor: theme.hover,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginTop: 7,
  },
  body: {
    flex: 1,
  },
  title: {
    fontSize: 15,
    fontWeight: '600',
    color: theme.textPrimary,
    lineHeight: 21,
    marginBottom: 4,
  },
  meta: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: 8,
  },
  source: {
    fontSize: 12,
    fontWeight: '600',
    color: theme.textSecondary,
  },
  time: {
    fontSize: 12,
    color: theme.textTertiary,
  },
  tagContainer: {
    backgroundColor: theme.accentMuted,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 3,
  },
  tag: {
    fontSize: 11,
    color: theme.accent,
    fontWeight: '500',
  },
  scoreBadge: {
    backgroundColor: theme.accentMuted,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    marginTop: 4,
  },
  scoreText: {
    fontSize: 12,
    fontWeight: '600',
    color: theme.accent,
  },
});
