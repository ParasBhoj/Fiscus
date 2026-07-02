import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, FlatList, Pressable, StyleSheet,
  ActivityIndicator, RefreshControl, TextInput,
} from 'react-native';
import { useRouter } from 'expo-router';
import { theme, getImpactColor } from '@/constants/theme';
import { fetchUpdates, searchUpdates, type RegulatoryUpdate } from '@/constants/api';
import FeedItem from '@/components/FeedItem';

const FILTERS = ['All', 'RBI', 'SEBI', 'High', 'Medium', 'Low'] as const;

export default function FeedScreen() {
  const router = useRouter();
  const [data, setData] = useState<RegulatoryUpdate[]>([]);
  const [filtered, setFiltered] = useState<RegulatoryUpdate[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeFilter, setActiveFilter] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const updates = await fetchUpdates(100);
      setData(updates);
      applyFilter(updates, activeFilter);
    } catch (err) {
      console.error('Failed to fetch:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [activeFilter]);

  useEffect(() => { loadData(); }, []);

  const onRefresh = () => {
    setRefreshing(true);
    setSearchQuery('');
    setIsSearching(false);
    loadData();
  };

  const applyFilter = (items: RegulatoryUpdate[], filter: string) => {
    if (filter === 'All') {
      setFiltered(items);
    } else if (filter === 'RBI' || filter === 'SEBI') {
      setFiltered(items.filter(i => i.source === filter));
    } else {
      setFiltered(items.filter(i => i.regulatory_impact === filter));
    }
  };

  const handleFilter = (filter: string) => {
    setActiveFilter(filter);
    setSearchQuery('');
    setIsSearching(false);
    applyFilter(data, filter);
  };

  const handleSearch = async () => {
    const q = searchQuery.trim();
    if (q.length < 2) {
      setIsSearching(false);
      applyFilter(data, activeFilter);
      return;
    }
    setIsSearching(true);
    setLoading(true);
    try {
      const results = await searchUpdates(q);
      setFiltered(results);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const openArticle = (item: RegulatoryUpdate) => {
    router.push({
      pathname: '/article/[id]',
      params: { id: item.id, data: JSON.stringify(item) },
    });
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.logo}>RegWatch</Text>
        <Text style={styles.subtitle}>Regulatory Intelligence</Text>
      </View>

      {/* Search */}
      <View style={styles.searchRow}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search with AI..."
          placeholderTextColor={theme.textTertiary}
          value={searchQuery}
          onChangeText={setSearchQuery}
          onSubmitEditing={handleSearch}
          returnKeyType="search"
        />
      </View>

      {/* Filter Chips */}
      <View style={styles.filterRow}>
        {FILTERS.map(f => {
          const isActive = activeFilter === f && !isSearching;
          const isImpact = f === 'High' || f === 'Medium' || f === 'Low';
          return (
            <Pressable
              key={f}
              style={[styles.filterChip, isActive && styles.filterChipActive]}
              onPress={() => handleFilter(f)}
            >
              {isImpact && (
                <View style={[styles.filterDot, { backgroundColor: getImpactColor(f) }]} />
              )}
              <Text style={[styles.filterText, isActive && styles.filterTextActive]}>
                {f}
              </Text>
            </Pressable>
          );
        })}
      </View>

      {/* Status */}
      {isSearching && (
        <Text style={styles.searchStatus}>
          {filtered.length} results for "{searchQuery}"
        </Text>
      )}

      {/* Feed List */}
      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color={theme.accent} />
        </View>
      ) : (
        <FlatList
          data={filtered}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <FeedItem
              item={item}
              onPress={() => openArticle(item)}
              showScore={isSearching}
            />
          )}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor={theme.accent}
              colors={[theme.accent]}
              progressBackgroundColor={theme.surface}
            />
          }
          ListEmptyComponent={
            <View style={styles.center}>
              <Text style={styles.emptyText}>No updates found.</Text>
              <Text style={styles.emptyHint}>Pull down to refresh.</Text>
            </View>
          }
          contentContainerStyle={filtered.length === 0 ? { flex: 1 } : undefined}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.bg,
  },
  header: {
    paddingTop: 56,
    paddingHorizontal: 16,
    paddingBottom: 8,
    backgroundColor: theme.surfaceAlt,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: theme.border,
  },
  logo: {
    fontSize: 24,
    fontWeight: '700',
    color: theme.textPrimary,
    letterSpacing: -0.5,
  },
  subtitle: {
    fontSize: 13,
    color: theme.textTertiary,
    marginTop: 2,
  },
  searchRow: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    backgroundColor: theme.surfaceAlt,
  },
  searchInput: {
    backgroundColor: theme.surface,
    borderWidth: 1,
    borderColor: theme.border,
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 14,
    color: theme.textPrimary,
  },
  filterRow: {
    flexDirection: 'row',
    paddingHorizontal: 12,
    paddingVertical: 8,
    gap: 6,
    backgroundColor: theme.surfaceAlt,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: theme.border,
  },
  filterChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 6,
    backgroundColor: theme.hover,
  },
  filterChipActive: {
    backgroundColor: theme.active,
  },
  filterDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  filterText: {
    fontSize: 12,
    fontWeight: '500',
    color: theme.textSecondary,
  },
  filterTextActive: {
    color: theme.accent,
  },
  searchStatus: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    fontSize: 13,
    color: theme.textTertiary,
    backgroundColor: theme.bg,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyText: {
    fontSize: 16,
    color: theme.textSecondary,
    marginBottom: 4,
  },
  emptyHint: {
    fontSize: 13,
    color: theme.textTertiary,
  },
});
