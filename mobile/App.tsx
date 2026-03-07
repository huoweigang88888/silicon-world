/**
 * Silicon World Mobile App
 * 硅基世界移动端应用
 */

import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { SafeAreaProvider } from 'react-native-safe-area-context';

// 屏幕组件
import HomeScreen from './src/screens/HomeScreen';
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import WalletScreen from './src/screens/WalletScreen';
import MessagesScreen from './src/screens/MessagesScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import AchievementsScreen from './src/screens/AchievementsScreen';
import LeaderboardScreen from './src/screens/LeaderboardScreen';

const Stack = createStackNavigator();

const App: React.FC = () => {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName="Login"
          screenOptions={{
            headerStyle: {
              backgroundColor: '#6200ee',
            },
            headerTintColor: '#fff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          }}
        >
          {/* 认证屏幕 */}
          <Stack.Screen 
            name="Login" 
            component={LoginScreen} 
            options={{ title: '登录' }} 
          />
          <Stack.Screen 
            name="Register" 
            component={RegisterScreen} 
            options={{ title: '注册' }} 
          />
          
          {/* 主屏幕 */}
          <Stack.Screen 
            name="Home" 
            component={HomeScreen} 
            options={{ title: '硅基世界' }} 
          />
          
          {/* 功能屏幕 */}
          <Stack.Screen 
            name="Wallet" 
            component={WalletScreen} 
            options={{ title: '钱包' }} 
          />
          <Stack.Screen 
            name="Messages" 
            component={MessagesScreen} 
            options={{ title: '消息' }} 
          />
          <Stack.Screen 
            name="Profile" 
            component={ProfileScreen} 
            options={{ title: '个人中心' }} 
          />
          <Stack.Screen 
            name="Achievements" 
            component={AchievementsScreen} 
            options={{ title: '成就' }} 
          />
          <Stack.Screen 
            name="Leaderboard" 
            component={LeaderboardScreen} 
            options={{ title: '排行榜' }} 
          />
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
};

export default App;
