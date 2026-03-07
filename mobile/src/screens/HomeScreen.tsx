/**
 * 主屏幕
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';

interface HomeScreenProps {
  navigation: any;
}

const HomeScreen: React.FC<HomeScreenProps> = ({ navigation }) => {
  const [refreshing, setRefreshing] = useState(false);
  const [userData, setUserData] = useState({
    name: '用户',
    level: 1,
    points: 0,
    achievements: 0,
  });

  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    // TODO: 刷新数据
    setTimeout(() => {
      setRefreshing(false);
    }, 2000);
  }, []);

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* 用户信息卡片 */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>欢迎回来，{userData.name}!</Text>
        <Text style={styles.cardSubtitle}>等级：{userData.level}</Text>
        <Text style={styles.cardSubtitle}>积分：{userData.points}</Text>
      </View>

      {/* 快捷操作 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>快捷操作</Text>
        <View style={styles.buttonRow}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('Wallet')}
          >
            <Text style={styles.actionButtonText}>💰 钱包</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('Messages')}
          >
            <Text style={styles.actionButtonText}>💬 消息</Text>
          </TouchableOpacity>
        </View>
        <View style={styles.buttonRow}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('Achievements')}
          >
            <Text style={styles.actionButtonText}>🏆 成就</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('Leaderboard')}
          >
            <Text style={styles.actionButtonText}>📊 排行榜</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* 最新动态 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>最新动态</Text>
        <View style={styles.newsItem}>
          <Text style={styles.newsTitle}>硅基世界 Week 8 更新</Text>
          <Text style={styles.newsDate}>2026-03-07</Text>
          <Text style={styles.newsContent}>
            游戏化系统上线！新增成就系统和排行榜...
          </Text>
        </View>
      </View>

      {/* 个人中心入口 */}
      <TouchableOpacity
        style={styles.profileButton}
        onPress={() => navigation.navigate('Profile')}
      >
        <Text style={styles.profileButtonText}>👤 进入个人中心</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  card: {
    backgroundColor: '#6200ee',
    margin: 16,
    padding: 20,
    borderRadius: 12,
    elevation: 4,
  },
  cardTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
  },
  cardSubtitle: {
    fontSize: 16,
    color: '#ffffff',
    opacity: 0.9,
    marginTop: 4,
  },
  section: {
    backgroundColor: '#ffffff',
    marginHorizontal: 16,
    marginBottom: 16,
    padding: 16,
    borderRadius: 12,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#333333',
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#6200ee',
    padding: 16,
    marginHorizontal: 4,
    borderRadius: 8,
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  newsItem: {
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eeeeee',
  },
  newsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333333',
  },
  newsDate: {
    fontSize: 12,
    color: '#999999',
    marginTop: 4,
  },
  newsContent: {
    fontSize: 14,
    color: '#666666',
    marginTop: 8,
  },
  profileButton: {
    backgroundColor: '#ffffff',
    margin: 16,
    padding: 16,
    borderRadius: 12,
    elevation: 2,
    alignItems: 'center',
  },
  profileButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#6200ee',
  },
});

export default HomeScreen;
