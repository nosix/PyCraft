# -*- coding: utf8 -*-

from collections import defaultdict


class ChunkInfo:
    """TerrainMap の各位置が持つ情報"""
    
    __slots__ = ['is_cached', '_scores', '_total', '_mob']

    def __init__(self):
        # 地形がキャッシュされているならば True
        self.is_cached = False
        # player_id:int -> score:int
        self._scores = {}
        # total of scores
        self._total = 0
        # MobEntity.eid
        self._mob = set()
    
    score = property(lambda self: self._total)

    def put_player(self, player_id, score):
        """Player を位置に設定する
        
        player_id : int - Player.player_id
        score : int - Player に近ければ高くなる値
        """
        self.remove_player(player_id)
        self._scores[player_id] = score
        self._total += score
    
    def remove_player(self, player_id):
        """Player を位置から取り除く
        
        player_id : int - Player.player_id
        """
        score = self._scores.pop(player_id, 0)
        self._total -= score

    def put_mob(self, eid):
        self._mob.add(eid)
    
    def remove_mob(self, eid):
        self._mob.discard(eid)
    
    def empty(self):
        """情報が空ならば True を返す"""
        return not self.is_cached and \
            len(self._scores) + len(self._animals) + len(self._monsters) == 0


class GroupByScore:
    
    CEILING_SCORE = 6

    def __init__(self):
        self._group = defaultdict(set)

    __slots__ = ['_group']

    def _ceil(self, score):
        return score \
            if score < self.CEILING_SCORE else self.CEILING_SCORE

    def append(self, chunk_pos, score):
        score = self._ceil(score)
        self._group[score].add(chunk_pos)

    def remove(self, chunk_pos, score):
        score = self._ceil(score)
        self._group[score].discard(chunk_pos)

    def find(self, scores):
        return (
            chunk_pos for score in scores 
                if score in self._group for chunk_pos in self._group[score])


class ChunkMap:
    """地図
    
    地形全体において Chunk 単位で Player の配置を記す。
    """
    
    MAX_SCORE_PER_PLAYER = GroupByScore.CEILING_SCORE

    def __init__(self):
        self._num_of_chunk = 0
        # ChunkPosition -> ChunkInfo
        self._info = defaultdict(ChunkInfo)
        # Entity.eid -> Position
        self._entity_pos = {}
        # score:int -> ChunkPosition
        self._group_by_score = GroupByScore()
    
    num_of_chunk = property(lambda self: self._num_of_chunk)

    def append(self, chunk_pos):
        """ChunkPosition が地形に追加されたとして記録する
        
        chunk_pos : ChunkPosition
        """
        self._info[chunk_pos].is_cached = True
        self._num_of_chunk += 1
    
    def pop(self):
        """スコアが最も低い ChunkPosition を返す
        
        渡した場所の情報は不要であれば破棄する。
        
        return : ChunkPosition
        """
        chunk_pos = self._find_cached_min_score()
        info = self._info[chunk_pos]
        info.is_cached = False
        assert not info.empty()
        self._num_of_chunk -= 1
        return chunk_pos

    def _find_cached_min_score(self):
        score = 0
        while score < self.MAX_SCORE_PER_PLAYER:
            for chunk_pos in self._group_by_score.find([score]):
                info = self._info[chunk_pos]
                if info.is_cached:
                    return chunk_pos
        assert False

    def find(self, scores):
        """条件を満たすスコアを持つ ChunkPosition を返す
        
        scores : sequence or iterable - 条件に指定するスコア
        """
        return (chunk_pos 
            for chunk_pos in self._group_by_score.find(scores) 
                if self._info[chunk_pos].is_cached)

    def score(self, pos):
        """指定した位置のスコア
        
        pos : Position - 調べる位置
        return : int - Player が近い程、密集している程、高くなる値
        """
        info = self._info[pos.chunk_pos]
        return info.score if info.is_cached else 0

    def has_chunk(self, pos_iterable):
        """指定された位置に Chunk があるならば True を返す
        """
        for pos in pos_iterable:
            chunk_pos = pos.chunk_pos
            if not chunk_pos in self._info \
                    or not self._info[chunk_pos].is_cached:
                return False
        return True

    def move_player(self, player):
        """Player を地図に配置し、地図上のスコアを更新する
        
        player : Player
        return : list(ChunkPlacement) - 
            Player を中心とする Chunk の位置、更新がなければ []
        """
        chunk_pos = player.pos.chunk_pos
        if player.eid in self._entity_pos:
            # ChunkPosition が変更されていなければ終了
            if chunk_pos == self._entity_pos[player.eid].chunk_pos:
                return []
            # 以前の ChunkPosition を更新
            self.remove_player(player)
        # 保持情報を更新
        self._entity_pos[player.eid] = player.pos
        max_priority = player.pos.CHUNK_AREA.PRIORITY_NUM
        rate = float(self.MAX_SCORE_PER_PLAYER) / max_priority
        surrounding_chunk = [p for p in player.pos.surrounding_chunk()]
        for priority, chunk_pos in surrounding_chunk:
            # スコア更新
            score = int((max_priority - priority) * rate)
            info = self._info[chunk_pos]
            self._group_by_score.remove(chunk_pos, info.score)
            info.put_player(player.player_id, score)
            self._group_by_score.append(chunk_pos, info.score)
        return surrounding_chunk
    
    def remove_player(self, player):
        """Player を地図から取り除き、地図上のスコアを更新する
        
        player : Player
        """
        if not player.eid in self._entity_pos:
            return
        def remove(chunk_pos):
            info = self._info[chunk_pos]
            self._group_by_score.remove(chunk_pos, info.score)
            info.remove_player(player.player_id)
            if info.empty():
                del self._info[chunk_pos]
            else:
                self._group_by_score.append(chunk_pos, info.score)
        pos = self._entity_pos.pop(player.eid)
        map(remove, (chunk_pos for _, chunk_pos in pos.surrounding_chunk()))

    def move_mob(self, entity):
        """Entity の移動を地図に反映する
        
        entity : Entity
        return : boolean - 更新したら True
        """
        chunk_pos = entity.pos.chunk_pos
        if entity.eid in self._entity_pos:
            # ChunkPosition が変更されていなければ終了
            if chunk_pos == self._entity_pos[entity.eid].chunk_pos:
                return False
            # 以前の ChunkPosition を更新
            self.remove_mob(entity)
        # 保持情報を更新
        self._entity_pos[entity.eid] = entity.pos
        info = self._info[chunk_pos]
        info.put_mob(entity.eid)
        return True

    def remove_mob(self, entity):
        """Entity を地図から削除する
        
        entity : Entity
        return : boolean - 更新したら True
        """
        # 情報が保持されていなければ終了
        if not entity.eid in self._entity_pos:
            return False
        # 保存された位置情報を取り除く
        pos = self._entity_pos.pop(entity.eid)
        # ChunkInfo を更新する
        chunk_pos = pos.chunk_pos
        info = self._info[chunk_pos]
        info.remove_mob(entity.eid)
        if info.empty():
            del self._info[chunk_pos]
        return True
