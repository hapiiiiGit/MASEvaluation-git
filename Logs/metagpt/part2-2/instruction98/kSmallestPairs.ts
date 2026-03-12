/**
 * Finds the k smallest pairs (one element from nums1 and one from nums2)
 * based on the sum of the pairs.
 *
 * @param nums1 - First sorted array of numbers.
 * @param nums2 - Second sorted array of numbers.
 * @param k - Number of smallest pairs to find.
 * @returns An array of pairs [numFromNums1, numFromNums2].
 */
export function kSmallestPairs(
  nums1: number[],
  nums2: number[],
  k: number
): [number, number][] {
  const result: [number, number][] = [];
  if (nums1.length === 0 || nums2.length === 0 || k === 0) return result;

  // Min-heap to store pairs by their sum.
  // Each element in heap: [sum, index1, index2]
  // We use a simple binary heap implementation here.
  class MinHeap {
    heap: Array<[number, number, number]> = [];

    private swap(i: number, j: number) {
      [this.heap[i], this.heap[j]] = [this.heap[j], this.heap[i]];
    }

    private bubbleUp(index: number) {
      while (index > 0) {
        const parent = Math.floor((index - 1) / 2);
        if (this.heap[parent][0] <= this.heap[index][0]) break;
        this.swap(parent, index);
        index = parent;
      }
    }

    private bubbleDown(index: number) {
      const length = this.heap.length;
      while (true) {
        let left = 2 * index + 1;
        let right = 2 * index + 2;
        let smallest = index;

        if (left < length && this.heap[left][0] < this.heap[smallest][0]) {
          smallest = left;
        }
        if (right < length && this.heap[right][0] < this.heap[smallest][0]) {
          smallest = right;
        }
        if (smallest === index) break;
        this.swap(index, smallest);
        index = smallest;
      }
    }

    push(item: [number, number, number]) {
      this.heap.push(item);
      this.bubbleUp(this.heap.length - 1);
    }

    pop(): [number, number, number] | undefined {
      if (this.heap.length === 0) return undefined;
      const top = this.heap[0];
      const end = this.heap.pop()!;
      if (this.heap.length > 0) {
        this.heap[0] = end;
        this.bubbleDown(0);
      }
      return top;
    }

    size(): number {
      return this.heap.length;
    }
  }

  const minHeap = new MinHeap();

  // Initialize heap with pairs (nums1[i], nums2[0]) for i in [0, min(k, nums1.length))
  // Because arrays are sorted, the smallest pairs must include nums2[0] initially.
  const len1 = nums1.length;
  const len2 = nums2.length;
  for (let i = 0; i < Math.min(k, len1); i++) {
    minHeap.push([nums1[i] + nums2[0], i, 0]);
  }

  while (result.length < k && minHeap.size() > 0) {
    const [sum, i, j] = minHeap.pop()!;
    result.push([nums1[i], nums2[j]]);
    // If there is a next element in nums2 for the current i, push the next pair
    if (j + 1 < len2) {
      minHeap.push([nums1[i] + nums2[j + 1], i, j + 1]);
    }
  }

  return result;
}