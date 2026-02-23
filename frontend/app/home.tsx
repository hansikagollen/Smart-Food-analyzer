import { View, Text, StyleSheet, TouchableOpacity, Alert, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import { useState, useEffect } from 'react';

export default function HomeScreen() {
  const router = useRouter();
  const [hasPermissions, setHasPermissions] = useState(false);

  useEffect(() => {
    requestPermissions();
  }, []);

  const requestPermissions = async () => {
    const cameraStatus = await ImagePicker.requestCameraPermissionsAsync();
    const galleryStatus = await ImagePicker.requestMediaLibraryPermissionsAsync();
    
    if (cameraStatus.status !== 'granted' || galleryStatus.status !== 'granted') {
      Alert.alert(
        'Permissions Required',
        'Camera and gallery access are needed to analyze food images.',
        [{ text: 'OK' }]
      );
    } else {
      setHasPermissions(true);
    }
  };

  const handleCaptureImage = async () => {
    try {
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: 'images',
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
        base64: true,
      });

      if (!result.canceled && result.assets[0]) {
        const imageUri = result.assets[0].uri;
        const base64 = result.assets[0].base64;
        router.push({
          pathname: '/loading',
          params: { imageUri, base64 }
        });
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to capture image. Please try again.');
      console.error('Camera error:', error);
    }
  };

  const handleUploadImage = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: 'images',
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
        base64: true,
      });

      if (!result.canceled && result.assets[0]) {
        const imageUri = result.assets[0].uri;
        const base64 = result.assets[0].base64;
        router.push({
          pathname: '/loading',
          params: { imageUri, base64 }
        });
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to select image. Please try again.');
      console.error('Gallery error:', error);
    }
  };

  const handleViewHistory = () => {
    router.push('/history');
  };

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.iconCircle}>
          <Text style={styles.iconText}>🥬</Text>
        </View>
        <Text style={styles.headerTitle}>Smart Food Quality</Text>
        <Text style={styles.headerSubtitle}>Analyzer</Text>
      </View>

      {/* Main Actions */}
      <View style={styles.actionsContainer}>
        <Text style={styles.instructionText}>Choose an option to analyze your food:</Text>
        
        {/* Capture Button */}
        <TouchableOpacity 
          style={[styles.actionButton, styles.primaryButton]}
          onPress={handleCaptureImage}
          activeOpacity={0.8}
        >
          <Ionicons name="camera" size={32} color="#ffffff" />
          <Text style={styles.buttonText}>Capture Image</Text>
          <Text style={styles.buttonSubtext}>Take a photo with camera</Text>
        </TouchableOpacity>

        {/* Upload Button */}
        <TouchableOpacity 
          style={[styles.actionButton, styles.secondaryButton]}
          onPress={handleUploadImage}
          activeOpacity={0.8}
        >
          <Ionicons name="images" size={32} color="#ffffff" />
          <Text style={styles.buttonText}>Upload from Gallery</Text>
          <Text style={styles.buttonSubtext}>Choose from your photos</Text>
        </TouchableOpacity>

        {/* History Button */}
        <TouchableOpacity 
          style={[styles.actionButton, styles.tertiaryButton]}
          onPress={handleViewHistory}
          activeOpacity={0.8}
        >
          <Ionicons name="time" size={32} color="#ffffff" />
          <Text style={styles.buttonText}>View History</Text>
          <Text style={styles.buttonSubtext}>See previous analyses</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  header: {
    alignItems: 'center',
    paddingTop: 60,
    paddingBottom: 30,
  },
  iconCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#16213e',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#0f3460',
    marginBottom: 15,
  },
  iconText: {
    fontSize: 40,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  headerSubtitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4ecca3',
  },
  actionsContainer: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 20,
  },
  instructionText: {
    fontSize: 16,
    color: '#a0a0a0',
    textAlign: 'center',
    marginBottom: 30,
  },
  actionButton: {
    borderRadius: 16,
    padding: 24,
    marginBottom: 16,
    alignItems: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  primaryButton: {
    backgroundColor: '#0f3460',
  },
  secondaryButton: {
    backgroundColor: '#16213e',
  },
  tertiaryButton: {
    backgroundColor: '#1a1a2e',
    borderWidth: 2,
    borderColor: '#4ecca3',
  },
  buttonText: {
    fontSize: 20,
    fontWeight: '600',
    color: '#ffffff',
    marginTop: 12,
  },
  buttonSubtext: {
    fontSize: 13,
    color: '#a0a0a0',
    marginTop: 4,
  },
});
