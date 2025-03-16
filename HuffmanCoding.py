import wave
import heapq
from collections import Counter
import os
import time
import random
import matplotlib.pyplot as plt



# Global variables
datas = []
data_range = 256
time_list = []
map_size_list = []



# Node for Huffman Tree
class HuffmanNode:
    def __init__(self, value, freq):
        self.value = value
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(data, fill_mode=False):
    frequency = Counter(data)
    heap = [HuffmanNode(value, freq) for value, freq in frequency.items()]
    if fill_mode:
        for i in range(data_range):
            if i not in frequency:
                heap.append(HuffmanNode(i, 0))
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    return heap[0]

def build_codes(node, prefix="", code_map=None):
    if code_map is None:
        code_map = {}

    if node is not None:
        if node.value is not None:
            code_map[node.value] = prefix
        build_codes(node.left, prefix + "0", code_map)
        build_codes(node.right, prefix + "1", code_map)

    return code_map



def huffman_encode(data, code_map):
    return ''.join(code_map[value] for value in data)

def huffman_decode(encoded_data, root):
    decoded_data = []
    current = root
    for bit in encoded_data:
        current = current.left if bit == '0' else current.right
        if current.value is not None:
            decoded_data.append(current.value)
            current = root

    return decoded_data

def huffman_encode_decode(input):
    # start_time = time.time()
    root = build_huffman_tree(input)
    code_map = build_codes(root)

    # Calculate the start time after building the tree and the map
    start_time = time.time()
    encoded_data = huffman_encode(input, code_map)
    decoded_data = huffman_decode(encoded_data, root)

    end_time = time.time()
    time_list.append(end_time - start_time)
    map_size_list.append(len(code_map))
    print("Time:", end_time - start_time)
    print("Map size:", len(code_map))

    if input == decoded_data:
        print("Data decoded successfully")
    print()



def load_data(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".wav"):
                datas.append(read_data(os.path.join(root, file)))

def read_data(path):
    data = []
    with wave.open(path, 'rb') as file:
        data = list(file.readframes(file.getnframes()))

        # metadata = file.getparams()
        # # print("Metadata:", metadata)
        # global data_range
        # data_range = pow(2, metadata.sampwidth * 8)
    return data



if __name__ == "__main__":
    path = "database"
    load_data(path)
    # print("Datas:", datas)
    # print("Datas length:", len(datas))
    data_len = len(datas)

    # Q1: Trade-off between Huffman table size and computational complexity
    input = []
    for data in datas:
        # print("Data:", data)
        # print("Data length:", len(data))
        input.extend(data)
    huffman_encode_decode(input)

    # '''
    time_list.clear()
    map_size_list.clear()
    for i in range(5):
        group_size = pow(2, i)
        input_grouped = [tuple(input[j:j+group_size]) for j in range(0, len(input), group_size)]
        huffman_encode_decode(input_grouped)

    # Draw the curve of time list and map size list vs i
    plt.figure(figsize=(12, 5))

    # Plot time list
    plt.subplot(1, 2, 1)
    plt.plot(range(5), time_list, marker='o', color='blue', label='Time')
    plt.title("Time vs i")
    plt.xlabel("i (Group Size = 2^i)")
    plt.ylabel("Time (seconds)")
    plt.grid(True)
    plt.legend()

    # Plot map size list
    plt.subplot(1, 2, 2)
    plt.plot(range(5), map_size_list, marker='o', color='green', label='Map Size')
    plt.title("Map Size vs i")
    plt.xlabel("i (Group Size = 2^i)")
    plt.ylabel("Map Size")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()
    # '''

    # Q2: How much training data do you need to build the Huffman table
    # '''
    # Take a look to every data's probability distribution
    random_indices = random.sample(range(data_len), 4)
    for idx in random_indices:
        data = datas[idx]
        frequency = Counter(data)
        
        # Plot histogram
        plt.figure(figsize=(10, 6))
        plt.bar(frequency.keys(), frequency.values(), color='blue', alpha=0.7)
        plt.title(f"Histogram for Randomly Selected Data {idx + 1}")
        plt.xlabel("Value")
        plt.ylabel("Frequency")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.show()

    # Test how many data do we need to build a good the Huffman table
    input_defective = datas[0]
    # input_defective = input
    time_list.clear()
    percentages = [i / 100 for i in range(1, 101)]
    for percentage in percentages:
        subset_size = int(len(input_defective) * percentage)
        subset = input_defective[:subset_size]

        root = build_huffman_tree(subset, True)
        code_map = build_codes(root)

        start_time = time.time()
        encoded_data = huffman_encode(input, code_map)
        decoded_data = huffman_decode(encoded_data, root)
        end_time = time.time()

        time_list.append(end_time - start_time)

    # Plot the curve of time list vs percentage
    plt.figure()
    plt.plot([p * 100 for p in percentages], time_list, marker='o', color='red', label='Time')
    plt.title("Time vs Percentage of Input")
    plt.xlabel("Percentage of Input (%)")
    plt.ylabel("Time (seconds)")
    plt.grid(True)
    plt.legend()
    plt.show()
    # '''

    # Q3: What happens when bits are lost
    # '''
    root = build_huffman_tree(input)
    code_map = build_codes(root)
    encoded_data = huffman_encode(input, code_map)

    # Randomly remove several bits from the encoded_data
    num_to_remove = 5 # Determine the number of bits that loss
    indices_to_remove = sorted(random.sample(range(len(encoded_data)), num_to_remove), reverse=True)
    encoded_data = ''.join(encoded_data[i] for i in range(len(encoded_data)) if i not in indices_to_remove)

    decoded_data = huffman_decode(encoded_data, root)

    if input == decoded_data:
        print("Data decoded successfully")
    else:
        print("Data decoded failed")
    # '''
