import React from 'react';
import {
  View, Text, ScrollView, Pressable, StyleSheet, Linking,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { theme, getImpactColor, getImpactBgColor, timeAgo } from '@/constants/theme';
import type { RegulatoryUpdate } from '@/constants/api';

export default function ArticleScreen() {
  const router = useRouter();
  const { data: dataStr } = useLocalSearchParams<{ id: string; data: string }>();

  let item: RegulatoryUpdate | null = null;
  try {
    item = JSON.parse(dataStr || '{}');
  } catch {
    item = null;
  }

  if (!item || !item.title) {
    return (
      <View style={[styles.container, styles.center]}>
        <Text style={styles.errorText}>Article not found.</Text>
        <Pressable onPress={() => router.back()}>
          <Text style={styles.backLink}>← Go back</Text>
        </Pressable>
      </View>
    );
  }

  const impactColor = getImpactColor(item.regulatory_impact);
  const impactBg = getImpactBgColor(item.regulatory_impact);
  const entities = (item.affected_entities || '')
    .split(',')
    .map(e => e.trim())
    .filter(e => e);

  const dateStr = item.publishedAt
    ? new Date(item.publishedAt).toLocaleDateString('en-IN', {
        weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
      })
    : item.rawPublishedAt || '';

  return (
    <View style={styles.container}>
      {/* Header Bar */}
      <View style={styles.headerBar}>
        <Pressable onPress={() => router.back()} hitSlop={12}>
          <Text style={styles.backBtn}>← Back</Text>
        </Pressable>
        <Pressable onPress={() => item?.url && Linking.openURL(item.url)}>
          <Text style={styles.sourceLink}>Open source ↗</Text>
        </Pressable>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent}>
        {/* Meta Bar */}
        <View style={styles.metaBar}>
          <Text style={styles.sourceLabel}>{item.source}</Text>
          <Text style={styles.dateLabel}>{dateStr}</Text>
          <View style={[styles.impactBadge, { backgroundColor: impactBg }]}>
            <Text style={[styles.impactText, { color: impactColor }]}>
              {item.regulatory_impact || 'Unknown'}
            </Text>
          </View>
        </View>

        {/* Title */}
        <Text style={styles.title}>{item.title}</Text>

        {/* Entity Tags */}
        {entities.length > 0 && (
          <View style={styles.tagsRow}>
            {entities.map((e, i) => (
              <View key={i} style={styles.tag}>
                <Text style={styles.tagText}>{e}</Text>
              </View>
            ))}
          </View>
        )}

        {/* AI Summary Box */}
        <View style={styles.summaryBox}>
          <Text style={styles.summaryLabel}>AI SUMMARY</Text>
          <Text style={styles.summaryText}>
            {item.summary || 'No summary available.'}
          </Text>
        </View>

        {/* Divider */}
        <View style={styles.divider} />

        {/* Full Text */}
        <Text style={styles.fullText}>
          {item.raw_text || 'Full text not available. Tap "Open source" above to read on the original website.'}
        </Text>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.surface,
  },
  center: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    fontSize: 16,
    color: theme.textSecondary,
    marginBottom: 12,
  },
  backLink: {
    color: theme.accent,
    fontSize: 15,
    fontWeight: '500',
  },
  headerBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 52,
    paddingHorizontal: 16,
    paddingBottom: 12,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: theme.border,
    backgroundColor: theme.surfaceAlt,
  },
  backBtn: {
    fontSize: 15,
    color: theme.accent,
    fontWeight: '500',
  },
  sourceLink: {
    fontSize: 13,
    color: theme.accent,
    fontWeight: '500',
  },
  scroll: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 48,
  },
  metaBar: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 14,
  },
  sourceLabel: {
    fontSize: 12,
    fontWeight: '700',
    color: theme.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  dateLabel: {
    fontSize: 12,
    color: theme.textTertiary,
  },
  impactBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 4,
  },
  impactText: {
    fontSize: 11,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.4,
  },
  title: {
    fontSize: 22,
    fontWeight: '700',
    color: theme.textPrimary,
    lineHeight: 30,
    letterSpacing: -0.3,
    marginBottom: 12,
  },
  tagsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginBottom: 16,
  },
  tag: {
    backgroundColor: theme.accentMuted,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  tagText: {
    fontSize: 12,
    color: theme.accent,
    fontWeight: '500',
  },
  summaryBox: {
    backgroundColor: theme.bg,
    borderWidth: 1,
    borderColor: theme.border,
    borderRadius: 10,
    padding: 14,
    marginBottom: 16,
  },
  summaryLabel: {
    fontSize: 10,
    fontWeight: '700',
    color: theme.textTertiary,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: 6,
  },
  summaryText: {
    fontSize: 14,
    color: theme.textSecondary,
    lineHeight: 22,
  },
  divider: {
    height: StyleSheet.hairlineWidth,
    backgroundColor: theme.border,
    marginBottom: 16,
  },
  fullText: {
    fontSize: 14,
    color: theme.textSecondary,
    lineHeight: 24,
  },
});
