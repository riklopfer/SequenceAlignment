"""
beam_aligner
Author: Russell Klopfer
"""
import heapq


class Alignment:
    def __init__(self, final_node, source_seq, target_seq):
        self.nodes = final_node.flatten()
        self.nodes.reverse()

        self.source_seq = source_seq
        self.target_seq = target_seq
        self.cost = final_node.cost

    def size(self):
        return len(self.nodes)

    def get_source(self, align_x):
        return self.source_seq[self.nodes[align_x].sourcePos]

    def get_target(self, align_x):
        return self.target_seq[self.nodes[align_x].targetPos]

    def get_type(self, align_x):
        return self.nodes[align_x].align_type

    def __str__(self):
        return ("size={} len(source)={}, len(target)={}, cost={}"
                .format(self.size(), len(self.source_seq), len(self.target_seq), self.cost)
                )

    def pretty_print(self):
        pretty = self.__str__() + "\n"
        for i in xrange(self.size()):
            type = self.get_type(i)
            source = '' if type == AlignmentType.INS else self.get_source(i)
            target = '' if type == AlignmentType.DEL else self.get_target(i)
            pretty += "{:<30}{:^10}{:>30}\n".format(source, type, target)
        return pretty


class AlignmentType:
    def __init__(self):
        raise AssertionError("Cannot instantiate this 'enum' type")

    START = "START"
    MATCH = "MATCH"
    SUB = "SUB"
    INS = "INS"
    DEL = "DEL"


class AlignmentNode:
    def __init__(self, align_type, previous, source_pos, target_pos, cost):
        """

        :rtype: AlignmentNode
        """
        self.align_type = align_type
        self.previous = previous
        self.cost = cost
        self.sourcePos = source_pos
        self.targetPos = target_pos

    def flatten(self):
        """
        Flatten the linked nodes into a list.
        :return:
        :rtype: list
        """
        flat = []
        current = self
        while current != Aligner.START_NODE:
            flat.append(current)
            current = current.previous
        return flat

    def __eq__(self, other):
        return (
            self.previous == other.previous and
            self.cost == other.cost and
            self.sourcePos == other.sourcePos and
            self.targetPos == other.targetPos
        )

    def __lt__(self, other):
        return self.cost < other.cost

    def __le__(self, other):
        return self.cost <= other.cost

    def __str__(self):
        return "{type: %s, source_pos: %d, target_pos: %d, cost: %d}" % (
            self.align_type, self.sourcePos, self.targetPos, self.cost)


def print_heap(heap):
    print "HEAP ({}) [[[".format(len(heap))
    for n in heap:
        print n
    print "]]]"


class Aligner:
    START_NODE = AlignmentNode(AlignmentType.START, None, -1, -1, 0)

    def __init__(self, beam_size, sub_cost=.9, ins_cost=1, del_cost=1):
        """
        Construct a new aligner with the given parameters.

        :param beam_size: keep the N-best alignments at each position
        :param sub_cost: cost of substituting one token for another
        :param ins_cost: cost of inserting a token (something in target that isn't in source)
        :param del_cost: cost of deleting a token (something in source that isn't in target)
        :return: a new Aligner object
        :rtype: Aligner
        """
        assert beam_size > 0, "beam_size must be > 0"

        self.beam_size = beam_size
        self.sub_cost = sub_cost
        self.ins_cost = ins_cost
        self.del_cost = del_cost

    def align(self, source, target):
        """

        :param source:
        :param target:
        :return:
        :rtype: Alignment
        """
        heap = [Aligner.START_NODE]

        while heap[0].sourcePos < len(source) - 1 or heap[0].targetPos < len(target) - 1:
            # print_heap(heap)
            next_heap = []
            for node in heap:
                self.__populate_nodes(next_heap, node, source, target)
            heap = next_heap[:min(self.beam_size, len(next_heap))]

        return Alignment(heap[0], source, target)

    def __populate_nodes(self, heap, previous_node, source, target):
        source_x = previous_node.sourcePos
        target_x = previous_node.targetPos
        cost = previous_node.cost

        def insertion():
            return AlignmentNode(AlignmentType.INS, previous_node, source_x, target_x + 1, cost + self.ins_cost)

        def deletion():
            return AlignmentNode(AlignmentType.DEL, previous_node, source_x + 1, target_x, cost + self.del_cost)

        def match():
            return AlignmentNode(AlignmentType.MATCH, previous_node, source_x + 1, target_x + 1, cost)

        def substitution():
            return AlignmentNode(AlignmentType.SUB, previous_node, source_x + 1, target_x + 1, cost + self.sub_cost)

        # we're at the end of the source sequence, this must be an insertion
        if source_x >= len(source) - 1:
            heapq.heappush(heap, insertion())
            return

        # we're at the end of the target sequence, this must be a deletion
        if target_x >= len(target) - 1:
            heapq.heappush(heap, deletion())
            return

        # match
        if source[source_x + 1] == target[target_x + 1]:
            heapq.heappush(heap, match())
        # sub
        else:
            heapq.heappush(heap, substitution())

        # always allow for insertions
        heapq.heappush(heap, insertion())
        # and deletions
        heapq.heappush(heap, deletion())
