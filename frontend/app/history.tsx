import { View, Text, StyleSheet, FlatList, TouchableOpacity, Image, Alert } from 'react-native';
import { useRouter, useFocusEffect } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useState, useCallback } from 'react';

interface HistoryItem {
  id: string;
  timestamp: string;
  food_name: string;
  freshness_class: string;
  image_base64: string;
  nutrition: {
    calories: number;
    carbs: number;
    protein: number;
  };
}

export default function HistoryScreen() {
  const router = useRouter();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useFocusEffect(
    useCallback(() => {
      loadHistory();
    }, [])
  );

  const loadHistory = async () => {
    try {
      setLoading(true);
      const historyData = await AsyncStorage.getItem('foodHistory');
      if (historyData) {
        const parsed = JSON.parse(historyData);
        setHistory(parsed);
      } else {
        setHistory([]);
      }
    } catch (error) {
      console.error('Failed to load history:', error);
      Alert.alert('Error', 'Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = () => {
    Alert.alert(
      'Clear History',
      'Are you sure you want to delete all history?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear',
          style: 'destructive',
          onPress: async () => {
            try {
              await AsyncStorage.removeItem('foodHistory');
              setHistory([]);
            } catch (error) {
              Alert.alert('Error', 'Failed to clear history');
            }
          },
        },
      ]
    );
  };

  const deleteItem = (id: string) => {
    Alert.alert(
      'Delete Item',
      'Remove this item from history?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              const updatedHistory = history.filter(item => item.id !== id);
              await AsyncStorage.setItem('foodHistory', JSON.stringify(updatedHistory));
              setHistory(updatedHistory);
            } catch (error) {
              Alert.alert('Error', 'Failed to delete item');
            }
          },
        },
      ]
    );
  };

  const getFreshnessColor = (freshness: string) => {
    switch (freshness) {
      case 'Fresh':
        return '#4ecca3';
      case 'Semi-Rotten':
        return '#ffd700';
      case 'Rotten':
        return '#ff6b6b';
      default:
        return '#a0a0a0';
    }
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const renderHistoryItem = ({ item }: { item: HistoryItem }) => (
    <TouchableOpacity
      style={styles.historyItem}
      onPress={() => {
        router.push({
          pathname: '/result',
          params: {
            imageUri: `data:image/jpeg;base64,${item.image_base64}`,
            data: JSON.stringify(item),
          },
        });
      }}
      activeOpacity={0.7}
    >
      <Image
        source={{ uri: `data:image/jpeg;base64,${item.image_base64}` }}
        style={styles.historyImage}
      />
      <View style={styles.historyContent}>
        <View style={styles.historyHeader}>
          <Text style={styles.historyFoodName}>{item.food_name}</Text>
          <TouchableOpacity onPress={() => deleteItem(item.id)} style={styles.deleteButton}>
            <Ionicons name="trash-outline" size={18} color="#ff6b6b" />
          </TouchableOpacity>
        </View>
        <View style={[styles.historyFreshnessBadge, { backgroundColor: getFreshnessColor(item.freshness_class) }]}>
          <Text style={styles.historyFreshnessText}>{item.freshness_class}</Text>
        </View>
        <Text style={styles.historyNutrition}>
          {item.nutrition.calories} cal • {item.nutrition.carbs}g carbs • {item.nutrition.protein}g protein
        </Text>
        <Text style={styles.historyTimestamp}>{formatDate(item.timestamp)}</Text>
      </View>
    </TouchableOpacity>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <Ionicons name="folder-open-outline" size={80} color="#a0a0a0" />
      <Text style={styles.emptyTitle}>No History Yet</Text>
      <Text style={styles.emptyText}>Start analyzing food to see your history here</Text>
      <TouchableOpacity style={styles.startButton} onPress={() => router.push('/home')}>
        <Text style={styles.startButtonText}>Analyze Food</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#ffffff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>History</Text>
        {history.length > 0 && (
          <TouchableOpacity onPress={clearHistory} style={styles.clearButton}>
            <Text style={styles.clearButtonText}>Clear</Text>
          </TouchableOpacity>
        )}
        {history.length === 0 && <View style={{ width: 60 }} />}
      </View>

      {/* History List */}
      {loading ? (
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading...</Text>
        </View>
      ) : (
        <FlatList
          data={history}
          renderItem={renderHistoryItem}
          keyExtractor={(item) => item.id}
          contentContainerStyle={history.length === 0 ? styles.emptyListContainer : styles.listContainer}
          ListEmptyComponent={renderEmptyState}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingTop: 50,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#16213e',
  },
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  clearButton: {
    padding: 8,
  },
  clearButtonText: {
    fontSize: 14,
    color: '#ff6b6b',
    fontWeight: '600',
  },
  listContainer: {
    padding: 16,
  },
  emptyListContainer: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#a0a0a0',
  },
  historyItem: {
    flexDirection: 'row',
    backgroundColor: '#16213e',
    borderRadius: 12,
    marginBottom: 16,
    overflow: 'hidden',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
  },
  historyImage: {
    width: 100,
    height: 120,
  },
  historyContent: {
    flex: 1,
    padding: 12,
    justifyContent: 'space-between',
  },
  historyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  historyFoodName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
    flex: 1,
  },
  deleteButton: {
    padding: 4,
  },
  historyFreshnessBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    marginTop: 6,
  },
  historyFreshnessText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#ffffff',
  },
  historyNutrition: {
    fontSize: 12,
    color: '#a0a0a0',
    marginTop: 6,
  },
  historyTimestamp: {
    fontSize: 11,
    color: '#4ecca3',
    marginTop: 4,
  },
  emptyContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 40,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginTop: 24,
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 16,
    color: '#a0a0a0',
    textAlign: 'center',
    marginBottom: 32,
  },
  startButton: {
    backgroundColor: '#0f3460',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 12,
  },
  startButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
});
