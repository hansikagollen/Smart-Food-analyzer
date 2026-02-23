import { View, Text, StyleSheet, Image, ActivityIndicator } from 'react-native';
import { useEffect, useRef } from 'react';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import axios from 'axios';
import Constants from 'expo-constants';

const EXPO_PUBLIC_BACKEND_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL;

export default function LoadingScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const { imageUri, base64 } = params;
  const hasProcessed = useRef(false);

  useEffect(() => {
    if (!hasProcessed.current) {
      hasProcessed.current = true;
      analyzeFoodImage();
    }
  }, []);

  const analyzeFoodImage = async () => {
    try {
      // Convert base64 to blob
      const base64Data = base64 as string;
      const byteCharacters = atob(base64Data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'image/jpeg' });

      // Create FormData
      const formData = new FormData();
      formData.append('file', blob as any, 'image.jpg');

      // Send to backend
      const apiUrl = `${EXPO_PUBLIC_BACKEND_URL}/api/predict`;
      console.log('Sending request to:', apiUrl);
      
      const response = await axios.post(apiUrl, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000,
      });

      console.log('Prediction response:', response.data);

      // Navigate to result screen with prediction data
      router.replace({
        pathname: '/result',
        params: {
          imageUri: imageUri as string,
          data: JSON.stringify(response.data),
        },
      });
    } catch (error) {
      console.error('Analysis error:', error);
      router.replace({
        pathname: '/result',
        params: {
          imageUri: imageUri as string,
          error: 'Failed to analyze image. Please try again.',
        },
      });
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      {/* Image Preview */}
      <View style={styles.imageContainer}>
        <Image 
          source={{ uri: imageUri as string }} 
          style={styles.image}
          resizeMode="cover"
        />
        <View style={styles.overlay} />
      </View>

      {/* Loading Content */}
      <View style={styles.loadingContent}>
        <ActivityIndicator size="large" color="#4ecca3" />
        <Text style={styles.loadingText}>Analyzing Food...</Text>
        <Text style={styles.loadingSubtext}>Detecting freshness and nutritional value</Text>
        
        {/* Progress Steps */}
        <View style={styles.stepsContainer}>
          <Text style={styles.stepText}>✓ Image received</Text>
          <Text style={styles.stepText}>⟳ Running AI analysis</Text>
          <Text style={styles.stepText}>⧗ Calculating nutrition</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  imageContainer: {
    width: '100%',
    height: '40%',
    position: 'relative',
  },
  image: {
    width: '100%',
    height: '100%',
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
  },
  loadingContent: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 24,
  },
  loadingText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginTop: 24,
  },
  loadingSubtext: {
    fontSize: 14,
    color: '#a0a0a0',
    marginTop: 8,
    textAlign: 'center',
  },
  stepsContainer: {
    marginTop: 40,
    alignItems: 'flex-start',
  },
  stepText: {
    fontSize: 14,
    color: '#4ecca3',
    marginVertical: 4,
  },
});
