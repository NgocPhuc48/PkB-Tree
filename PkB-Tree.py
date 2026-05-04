import time
import random
import statistics
import matplotlib.pyplot as plt
import numpy as np

class PkBTree:
    def __init__(self, name, use_pkb_opt=False):
        self.name = name
        self.use_pkb_opt = use_pkb_opt
        self.nodes = [] # Lưu trữ các bản ghi nén

    def _get_common_prefix_len(self, s1, s2):
        n = min(len(s1), len(s2))
        for i in range(n):
            if s1[i] != s2[i]: return i
        return n

    def insert(self, keys):
        self.nodes = []
        sorted_keys = sorted(keys)
        if not sorted_keys: return

        prev_key = ""
        for i, curr_key in enumerate(sorted_keys):
            if self.use_pkb_opt:

                p_len = self._get_common_prefix_len(prev_key, curr_key)
                
                separator = curr_key[:p_len + 1]
                suffix = separator[p_len:]
                
                self.nodes.append({'p_len': p_len, 'suffix': suffix})
                prev_key = curr_key
            else:
                self.nodes.append({'p_len': 0, 'suffix': curr_key})

    def search(self, keys):
        # Mô phỏng tìm kiếm trên cấu trúc PkB
        for k in keys:
            current_full = ""
            for node in self.nodes:
                # Giải nén nhanh bằng cách ghép Suffix vào đúng vị trí p_len
                current_full = current_full[:node['p_len']] + node['suffix']
                if k.startswith(current_full):
                    break
        return True

    def search_range(self, all_sorted, min_indices):
        for idx in min_indices:
            _ = all_sorted[idx : idx + 100]
        return True

# --- 2. Chạy Benchmark ---

def run_pkb_benchmark():
    key_numbers = 80000
    # Dữ liệu mô phỏng cấu trúc phân cấp (ví dụ: DNS records)
    all_data = [f"vn.edu.university.student.id_{i:06d}.records.internal" for i in range(key_numbers)]
    random.shuffle(all_data)
    
    values = all_data[15000:]
    values_warmup = all_data[:15000]
    all_sorted = sorted(all_data)
    min_indices = [random.randint(0, 60000) for _ in range(100)]

    structures = [
        PkBTree("Btree-Standard", use_pkb_opt=False),
        PkBTree("Btree-PkB-Opt", use_pkb_opt=True)
    ]
    
    results = {s.name: {t: [] for t in ["insert", "search", "range"]} for s in structures}

    for i in range(3):
        print(f"Thực hiện lần lặp {i+1}...")
        for tree in structures:
            t0 = time.perf_counter()
            tree.insert(values)
            results[tree.name]['insert'].append(time.perf_counter() - t0)
            
            t0 = time.perf_counter()
            tree.search(values[:3000]) # Tìm 3k mẫu
            results[tree.name]['search'].append(time.perf_counter() - t0)
            
            t0 = time.perf_counter()
            tree.search_range(all_sorted, min_indices)
            results[tree.name]['range'].append(time.perf_counter() - t0)

    return results, 65000

# --- 3. Trực quan hóa ---

def plot_pkb_results(results, n_ins):
    names = list(results.keys())
    ops = ['insert', 'search', 'range']
    data_points = {op: [] for op in ops}
    
    for name in names:
        for op in ops:
            avg_t = statistics.mean(results[name][op])
            count = 100 if op == 'range' else (n_ins if op == 'insert' else 3000)
            data_points[op].append(count / avg_t)

    x = np.arange(len(ops))
    width = 0.35
    fig, ax = plt.subplots(figsize=(12, 7))
    colors = ['#bdc3c7', '#8e44ad'] # Xám và Tím (PkB)

    for i, name in enumerate(names):
        vals = [data_points[op][i] for op in ops]
        rects = ax.bar(x + i*width, vals, width, label=name, color=colors[i], edgecolor='black')
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height/1e6:.2f}M', xy=(rect.get_x() + rect.get_width()/2, height),
                        xytext=(0, 3), textcoords="offset points", ha='center', fontweight='bold')

    ax.set_ylabel('Ops/sec (Triệu Ops)', fontweight='bold')
    ax.set_title('MÔ PHỎNG HIỆU NĂNG: PREFIX KEY B-TREE (PKB-TREE)', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels([o.upper() for o in ops], fontweight='bold')
    ax.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    res, n = run_pkb_benchmark()
    plot_pkb_results(res, n)