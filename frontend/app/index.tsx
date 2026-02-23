import { View, Text, StyleSheet, Image } from 'react-native';
import { useEffect } from 'react';
import { useRouter } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

export default function SplashScreen() {
  const router = useRouter();

  useEffect(() => {
    // Navigate to home after 2.5 seconds
    const timer = setTimeout(() => {
      router.replace('/home');
    }, 2500);

    return () => clearTimeout(timer);
  }, []);

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      {/* App Logo/Icon */}
      <View style={styles.logoContainer}>
        <View style={styles.iconCircle}>
          <Text style={styles.iconText}>🥬</Text>
        </View>
      </View>

      {/* App Name */}
      <Text style={styles.title}>Smart Food Quality</Text>
      <Text style={styles.subtitle}>Analyzer</Text>
      
      {/* Tagline */}
      <Text style={styles.tagline}>AI-Powered Freshness Detection</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoContainer: {
    marginBottom: 30,
  },
  iconCircle: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#16213e',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 3,
    borderColor: '#0f3460',
  },
  iconText: {
    fontSize: 60,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ffffff',
    marginTop: 20,
  },
  subtitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#4ecca3',
    marginBottom: 10,
  },
  tagline: {
    fontSize: 14,
    color: '#a0a0a0',
    marginTop: 8,
  },
});
