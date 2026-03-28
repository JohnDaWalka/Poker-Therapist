"""
Statistics Tracking Module - Track user progress and generate reports
"""

import json
import os
from datetime import datetime
from typing import Dict, List


class StatisticsTracker:
    """Track training statistics and progress"""
    
    def __init__(self, storage_path: str = 'stats_data.json'):
        self.storage_path = storage_path
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict:
        """Load statistics from file"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return self._create_empty_stats()
        return self._create_empty_stats()
    
    def _create_empty_stats(self) -> Dict:
        """Create empty statistics structure"""
        return {
            'users': {},
            'sessions': [],
            'global_stats': {
                'total_hands_played': 0,
                'total_training_sessions': 0,
                'total_equity_calculations': 0
            }
        }
    
    def _save_stats(self):
        """Save statistics to file"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Error saving stats: {e}")
    
    def get_or_create_user(self, user_id: str) -> Dict:
        """Get or create user statistics"""
        if user_id not in self.stats['users']:
            self.stats['users'][user_id] = {
                'user_id': user_id,
                'created_at': datetime.now().isoformat(),
                'training_sessions': [],
                'hand_evaluations': {
                    'total': 0,
                    'correct': 0,
                    'incorrect': 0,
                    'by_hand_type': {}
                },
                'equity_calculations': {
                    'total': 0,
                    'by_game_type': {}
                },
                'gto_training': {
                    'scenarios_practiced': [],
                    'correct_decisions': 0,
                    'total_decisions': 0
                }
            }
        return self.stats['users'][user_id]
    
    def record_training_session(self, user_id: str, session_data: Dict):
        """Record a training session"""
        user = self.get_or_create_user(user_id)
        
        session = {
            'timestamp': datetime.now().isoformat(),
            'game_type': session_data.get('game_type', 'holdem'),
            'correct': session_data.get('correct', False),
            'hand_type': session_data.get('hand_type', 'unknown'),
            'duration_seconds': session_data.get('duration', 0)
        }
        
        user['training_sessions'].append(session)
        
        # Update statistics
        user['hand_evaluations']['total'] += 1
        if session_data.get('correct', False):
            user['hand_evaluations']['correct'] += 1
        else:
            user['hand_evaluations']['incorrect'] += 1
        
        hand_type = session_data.get('hand_type', 'unknown')
        if hand_type not in user['hand_evaluations']['by_hand_type']:
            user['hand_evaluations']['by_hand_type'][hand_type] = {'correct': 0, 'total': 0}
        
        user['hand_evaluations']['by_hand_type'][hand_type]['total'] += 1
        if session_data.get('correct', False):
            user['hand_evaluations']['by_hand_type'][hand_type]['correct'] += 1
        
        self.stats['global_stats']['total_training_sessions'] += 1
        self._save_stats()
    
    def record_equity_calculation(self, user_id: str, game_type: str = 'holdem', 
                                  players: int = 2):
        """Record an equity calculation"""
        user = self.get_or_create_user(user_id)
        user['equity_calculations']['total'] += 1
        
        if game_type not in user['equity_calculations']['by_game_type']:
            user['equity_calculations']['by_game_type'][game_type] = 0
        user['equity_calculations']['by_game_type'][game_type] += 1
        
        self.stats['global_stats']['total_equity_calculations'] += 1
        self._save_stats()
    
    def record_gto_decision(self, user_id: str, scenario: str, correct: bool):
        """Record a GTO training decision"""
        user = self.get_or_create_user(user_id)
        
        if scenario not in user['gto_training']['scenarios_practiced']:
            user['gto_training']['scenarios_practiced'].append(scenario)
        
        user['gto_training']['total_decisions'] += 1
        if correct:
            user['gto_training']['correct_decisions'] += 1
        
        self._save_stats()
    
    def get_user_report(self, user_id: str) -> Dict:
        """Generate a progress report for a user"""
        if user_id not in self.stats['users']:
            return {'error': 'User not found'}
        
        user = self.stats['users'][user_id]
        
        # Calculate accuracy
        total_hands = user['hand_evaluations']['total']
        correct_hands = user['hand_evaluations']['correct']
        accuracy = (correct_hands / total_hands * 100) if total_hands > 0 else 0
        
        # GTO accuracy
        gto_total = user['gto_training']['total_decisions']
        gto_correct = user['gto_training']['correct_decisions']
        gto_accuracy = (gto_correct / gto_total * 100) if gto_total > 0 else 0
        
        # Recent sessions (last 10)
        recent_sessions = user['training_sessions'][-10:]
        
        # Performance by hand type
        hand_type_performance = {}
        for hand_type, data in user['hand_evaluations']['by_hand_type'].items():
            if data['total'] > 0:
                accuracy = (data['correct'] / data['total'] * 100)
                hand_type_performance[hand_type] = {
                    'total': data['total'],
                    'correct': data['correct'],
                    'accuracy': round(accuracy, 1)
                }
        
        return {
            'user_id': user_id,
            'created_at': user['created_at'],
            'summary': {
                'total_training_sessions': len(user['training_sessions']),
                'overall_accuracy': round(accuracy, 1),
                'total_hands_evaluated': total_hands,
                'correct_evaluations': correct_hands,
                'equity_calculations': user['equity_calculations']['total']
            },
            'gto_training': {
                'scenarios_practiced': len(user['gto_training']['scenarios_practiced']),
                'total_decisions': gto_total,
                'correct_decisions': gto_correct,
                'accuracy': round(gto_accuracy, 1)
            },
            'performance_by_hand_type': hand_type_performance,
            'recent_sessions': recent_sessions
        }
    
    def get_global_stats(self) -> Dict:
        """Get global statistics across all users"""
        return {
            'total_users': len(self.stats['users']),
            'total_training_sessions': self.stats['global_stats']['total_training_sessions'],
            'total_equity_calculations': self.stats['global_stats']['total_equity_calculations'],
            'total_hands_played': self.stats['global_stats']['total_hands_played']
        }


class MultiplayerSessionManager:
    """Manage multiplayer training sessions"""
    
    def __init__(self):
        self.sessions = {}
        self.session_counter = 0
    
    def create_session(self, creator_id: str, session_type: str = 'equity', 
                      max_players: int = 4) -> str:
        """Create a new multiplayer session"""
        self.session_counter += 1
        session_id = f"mp_{self.session_counter}"
        
        self.sessions[session_id] = {
            'session_id': session_id,
            'creator_id': creator_id,
            'session_type': session_type,
            'max_players': max_players,
            'players': [creator_id],
            'status': 'waiting',  # waiting, active, completed
            'created_at': datetime.now().isoformat(),
            'results': []
        }
        
        return session_id
    
    def join_session(self, session_id: str, player_id: str) -> Dict:
        """Join an existing session"""
        if session_id not in self.sessions:
            return {'error': 'Session not found'}
        
        session = self.sessions[session_id]
        
        if session['status'] != 'waiting':
            return {'error': 'Session is not accepting players'}
        
        if len(session['players']) >= session['max_players']:
            return {'error': 'Session is full'}
        
        if player_id in session['players']:
            return {'error': 'Already in session'}
        
        session['players'].append(player_id)
        return {'success': True, 'session': session}
    
    def start_session(self, session_id: str) -> Dict:
        """Start a multiplayer session"""
        if session_id not in self.sessions:
            return {'error': 'Session not found'}
        
        session = self.sessions[session_id]
        
        if len(session['players']) < 2:
            return {'error': 'Need at least 2 players to start'}
        
        session['status'] = 'active'
        session['started_at'] = datetime.now().isoformat()
        
        return {'success': True, 'session': session}
    
    def get_session(self, session_id: str) -> Dict:
        """Get session details"""
        if session_id not in self.sessions:
            return {'error': 'Session not found'}
        return self.sessions[session_id]
    
    def list_available_sessions(self) -> List[Dict]:
        """List all available sessions"""
        available = []
        for session_id, session in self.sessions.items():
            if session['status'] == 'waiting':
                available.append({
                    'session_id': session_id,
                    'creator': session['creator_id'],
                    'type': session['session_type'],
                    'players': len(session['players']),
                    'max_players': session['max_players']
                })
        return available
    
    def record_result(self, session_id: str, player_id: str, result: Dict):
        """Record a result for a player in a session"""
        if session_id not in self.sessions:
            return {'error': 'Session not found'}
        
        session = self.sessions[session_id]
        
        result['player_id'] = player_id
        result['timestamp'] = datetime.now().isoformat()
        session['results'].append(result)
        
        return {'success': True}
    
    def end_session(self, session_id: str) -> Dict:
        """End a multiplayer session"""
        if session_id not in self.sessions:
            return {'error': 'Session not found'}
        
        session = self.sessions[session_id]
        session['status'] = 'completed'
        session['ended_at'] = datetime.now().isoformat()
        
        return {'success': True, 'results': session['results']}


# Global instances
stats_tracker = StatisticsTracker()
multiplayer_manager = MultiplayerSessionManager()
