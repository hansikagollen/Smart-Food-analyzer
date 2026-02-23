import { View, Text, StyleSheet, Image, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useEffect, useState } from 'react';

interface NutritionInfo {
  calories: number;
  carbs: number;
  protein: number;
  fat: number;
  fiber: number;
}

interface PredictionData {
  food_name: string;
  freshness_class: string;
  confidence: number;
  nutrition: NutritionInfo;
  bioactive_compounds: string[];
  health_benefits: string;
  image_base64: string;
}

export default function ResultScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const [saved, setSaved] = useState(false);

  const imageUri = params.imageUri as string;
  const errorMessage = params.error as string;
  
  let predictionData: PredictionData | null = null;
  if (params.data) {
    try {
      predictionData = JSON.parse(params.data as string);
    } catch (e) {
      console.error('Failed to parse prediction data:', e);
    }
  }

  useEffect(() => {
    if (predictionData) {
      saveToHistory();
    }
  }, []);

  const saveToHistory = async () => {
    try {
      if (!predictionData) return;

      const historyItem = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        imageUri,
        ...predictionData,
      };

      const existingHistory = await AsyncStorage.getItem('foodHistory');
      const history = existingHistory ? JSON.parse(existingHistory) : [];
      history.unshift(historyItem);
      
      // Keep only last 50 items
      const trimmedHistory = history.slice(0, 50);
      await AsyncStorage.setItem('foodHistory', JSON.stringify(trimmedHistory));
      setSaved(true);
    } catch (error) {
      console.error('Failed to save history:', error);
    }
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

  const getFreshnessIcon = (freshness: string) => {
    switch (freshness) {
      case 'Fresh':
        return 'checkmark-circle';
      case 'Semi-Rotten':
        return 'warning';
      case 'Rotten':
        return 'close-circle';
      default:
        return 'help-circle';
    }
  };

  if (errorMessage) {
    return (
      <View style={styles.container}>
        <StatusBar style="light" />
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle" size={80} color="#ff6b6b" />
          <Text style={styles.errorTitle}>Analysis Failed</Text>
          <Text style={styles.errorText}>{errorMessage}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={() => router.back()}>
            <Text style={styles.retryButtonText}>Try Again</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  if (!predictionData) {
    return (
      <View style={styles.container}>
        <StatusBar style="light" />
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle" size={80} color="#ff6b6b" />
          <Text style={styles.errorTitle}>Food Not Recognized</Text>
          <Text style={styles.errorText}>Unable to analyze this image. Please try with a clearer photo of a fruit or vegetable.</Text>
          <TouchableOpacity style={styles.retryButton} onPress={() => router.back()}>
            <Text style={styles.retryButtonText}>Try Again</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      {/* Header with back button */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.push('/home')} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#ffffff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Analysis Results</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Food Image */}
        <View style={styles.imageContainer}>
          <Image 
            source={{ uri: `data:image/jpeg;base64,${predictionData.image_base64}` }}
            style={styles.foodImage}
            resizeMode="cover"
          />
        </View>

        {/* Food Name & Freshness Badge */}
        <View style={styles.resultHeader}>
          <Text style={styles.foodName}>{predictionData.food_name}</Text>
          <View style={[styles.freshnessBadge, { backgroundColor: getFreshnessColor(predictionData.freshness_class) }]}>
            <Ionicons name={getFreshnessIcon(predictionData.freshness_class) as any} size={24} color="#ffffff" />
            <Text style={styles.freshnessText}>{predictionData.freshness_class}</Text>
          </View>
          <Text style={styles.confidenceText}>Confidence: {(predictionData.confidence * 100).toFixed(0)}%</Text>
        </View>

        {/* Nutrition Table */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Nutritional Information</Text>
          <View style={styles.nutritionGrid}>
            <View style={styles.nutritionItem}>
              <Ionicons name="flame" size={24} color="#ff6b6b" />
              <Text style={styles.nutritionValue}>{predictionData.nutrition.calories}</Text>
              <Text style={styles.nutritionLabel}>Calories</Text>
            </View>
            <View style={styles.nutritionItem}>
              <Ionicons name="nutrition" size={24} color="#4ecca3" />
              <Text style={styles.nutritionValue}>{predictionData.nutrition.carbs}g</Text>
              <Text style={styles.nutritionLabel}>Carbs</Text>
            </View>
            <View style={styles.nutritionItem}>
              <Ionicons name="fitness" size={24} color="#ffd700" />
              <Text style={styles.nutritionValue}>{predictionData.nutrition.protein}g</Text>
              <Text style={styles.nutritionLabel}>Protein</Text>
            </View>
            <View style={styles.nutritionItem}>
              <Ionicons name="water" size={24} color="#00d4ff" />
              <Text style={styles.nutritionValue}>{predictionData.nutrition.fat}g</Text>
              <Text style={styles.nutritionLabel}>Fat</Text>
            </View>
            <View style={styles.nutritionItem}>
              <Ionicons name="leaf" size={24} color="#7bed9f" />
              <Text style={styles.nutritionValue}>{predictionData.nutrition.fiber}g</Text>
              <Text style={styles.nutritionLabel}>Fiber</Text>
            </View>
          </View>
        </View>

        {/* Bioactive Compounds */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Bioactive Compounds</Text>
          <View style={styles.compoundsContainer}>
            {predictionData.bioactive_compounds.map((compound, index) => (
              <View key={index} style={styles.compoundTag}>
                <Text style={styles.compoundText}>{compound}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* Health Benefits */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Health Benefits</Text>
          <View style={styles.benefitsContainer}>
            <Ionicons name="heart" size={20} color="#ff6b6b" style={styles.benefitsIcon} />
            <Text style={styles.benefitsText}>{predictionData.health_benefits}</Text>
          </View>
        </View>

        {/* Action Buttons */}
        <View style={styles.actionButtons}>
          <TouchableOpacity 
            style={styles.primaryActionButton} 
            onPress={() => router.push('/home')}
          >
            <Ionicons name="camera" size={20} color="#ffffff" />
            <Text style={styles.actionButtonText}>Analyze Another</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.secondaryActionButton} 
            onPress={() => router.push('/history')}
          >
            <Ionicons name="time" size={20} color="#4ecca3" />
            <Text style={styles.secondaryActionButtonText}>View History</Text>
          </TouchableOpacity>
        </View>

        <View style={{ height: 40 }} />
      </ScrollView>
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
  },
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
  },
  scrollView: {
    flex: 1,
  },
  imageContainer: {
    width: '100%',
    height: 250,
    backgroundColor: '#16213e',
  },
  foodImage: {
    width: '100%',
    height: '100%',
  },
  resultHeader: {
    padding: 24,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#16213e',
  },
  foodName: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 16,
  },
  freshnessBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 25,
    marginBottom: 8,
  },
  freshnessText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
    marginLeft: 8,
  },
  confidenceText: {
    fontSize: 14,
    color: '#a0a0a0',
    marginTop: 8,
  },
  section: {
    padding: 24,
    borderBottomWidth: 1,
    borderBottomColor: '#16213e',
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 16,
  },
  nutritionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  nutritionItem: {
    width: '30%',
    alignItems: 'center',
    backgroundColor: '#16213e',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  nutritionValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginTop: 8,
  },
  nutritionLabel: {
    fontSize: 12,
    color: '#a0a0a0',
    marginTop: 4,
  },
  compoundsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  compoundTag: {
    backgroundColor: '#16213e',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#4ecca3',
  },
  compoundText: {
    fontSize: 14,
    color: '#4ecca3',
  },
  benefitsContainer: {
    flexDirection: 'row',
    backgroundColor: '#16213e',
    borderRadius: 12,
    padding: 16,
  },
  benefitsIcon: {
    marginRight: 12,
    marginTop: 2,
  },
  benefitsText: {
    flex: 1,
    fontSize: 15,
    color: '#ffffff',
    lineHeight: 22,
  },
  actionButtons: {
    padding: 24,
  },
  primaryActionButton: {
    flexDirection: 'row',
    backgroundColor: '#0f3460',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  actionButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    marginLeft: 8,
  },
  secondaryActionButton: {
    flexDirection: 'row',
    backgroundColor: 'transparent',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#4ecca3',
  },
  secondaryActionButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#4ecca3',
    marginLeft: 8,
  },
  errorContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 40,
  },
  errorTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginTop: 24,
    marginBottom: 12,
  },
  errorText: {
    fontSize: 16,
    color: '#a0a0a0',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
  },
  retryButton: {
    backgroundColor: '#0f3460',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 12,
  },
  retryButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
});
