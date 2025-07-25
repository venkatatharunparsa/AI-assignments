import heapq
from itertools import combinations

# --- BFS (Breadth-First Search using Priority Queue - Dijkstra's Algorithm) ---
def solve_bridge_problem_bfs(crossing_times, time_limit):
    """
    Solves the bridge crossing problem using a priority queue based BFS (Dijkstra's algorithm)
    to find the path with the minimum total time.
    """
    all_people = frozenset(crossing_times.keys())
    initial_state = (frozenset(all_people), frozenset(), 'start')  # (start_side, end_side, umbrella_pos)
    
    pq = [(0, [initial_state])]  # (current_time, path_to_state)
    visited_times = {initial_state: 0}  # Track best time to each state

    while pq:
        current_time, path = heapq.heappop(pq)
        current_config = path[-1]
        start_side, end_side, umbrella_pos = current_config

        if not start_side:
            if current_time <= time_limit:
                return current_time, path, visited_times
            else:
                continue  # Continue searching for better path

        if current_time > visited_times.get(current_config, float('inf')):
            continue

        if umbrella_pos == 'start':
            move_from = start_side
            move_to_pos = 'end'
        else:
            move_from = end_side
            move_to_pos = 'start'

        for num_people in [1, 2]:
            if len(move_from) < num_people:
                continue

            for group in combinations(move_from, num_people):
                group = frozenset(group)
                trip_time = max(crossing_times[person] for person in group)
                new_total_time = current_time + trip_time

                if new_total_time > time_limit:
                    continue

                if umbrella_pos == 'start':
                    new_start_side = start_side - group
                    new_end_side = end_side | group
                else:
                    new_start_side = start_side | group
                    new_end_side = end_side - group

                new_config = (new_start_side, new_end_side, move_to_pos)

                if new_config not in visited_times or new_total_time < visited_times[new_config]:
                    visited_times[new_config] = new_total_time
                    new_path = path + [new_config]
                    heapq.heappush(pq, (new_total_time, new_path))

    return None, None, visited_times


# --- DFS (Depth-First Search) Implementation ---
def solve_bridge_problem_dfs(crossing_times, time_limit):
    """
    Solves the bridge crossing problem using DFS to find the shortest path.
    """
    all_people = frozenset(crossing_times.keys())
    initial_state = (frozenset(all_people), frozenset(), 'start')

    stack = [(0, [initial_state], initial_state)]
    visited_states = {initial_state: 0}

    min_total_time = float('inf')
    best_path = None

    while stack:
        current_time, path, current_config = stack.pop()
        start_side, end_side, umbrella_pos = current_config

        if not start_side:
            if current_time < min_total_time and current_time <= time_limit:
                min_total_time = current_time
                best_path = path
            continue

        if current_time >= min_total_time or current_time > time_limit:
            continue

        if current_time > visited_states.get(current_config, float('inf')):
            continue

        if umbrella_pos == 'start':
            move_from = start_side
            move_to_pos = 'end'
        else:
            move_from = end_side
            move_to_pos = 'start'

        possible_moves = []
        for num_people in [1, 2]:
            if len(move_from) < num_people:
                continue

            for group in combinations(move_from, num_people):
                group = frozenset(group)
                trip_time = max(crossing_times[person] for person in group)
                new_total_time = current_time + trip_time

                if new_total_time > time_limit:
                    continue

                if umbrella_pos == 'start':
                    new_start_side = start_side - group
                    new_end_side = end_side | group
                else:
                    new_start_side = start_side | group
                    new_end_side = end_side - group

                new_config = (new_start_side, new_end_side, move_to_pos)

                if new_config not in visited_states or new_total_time < visited_states[new_config]:
                    visited_states[new_config] = new_total_time
                    possible_moves.append((new_total_time, path + [new_config], new_config))

        for move in sorted(possible_moves, key=lambda x: x[0], reverse=True):
            stack.append(move)

    return min_total_time if min_total_time != float('inf') else None, best_path, visited_states


# --- Utility Function for Printing Solutions ---
def print_bridge_solution(total_time, path, crossing_times, visited_times_map, algorithm_name):
    """
    Prints the steps of the bridge crossing solution.
    """
    print(f"\n--- {algorithm_name} Solution ---")
    if path:
        print(f"🎉 Solution found! Total time: {total_time} minutes.")
        print("-" * 40)
        for i in range(len(path) - 1):
            start_config = path[i]
            end_config = path[i + 1]
            time_at_step = visited_times_map[end_config]
            trip_time = time_at_step - visited_times_map[start_config]

            if start_config[2] == 'start':
                moved_people = start_config[0] - end_config[0]
                direction = "-->"
                action = "cross"
            else:
                moved_people = end_config[0] - start_config[0]
                direction = "<--"
                action = "return"

            people_str = " and ".join(sorted(moved_people))
            print(f"Step {i + 1}: {people_str} {action} {direction} ({trip_time} min)")
            print(f"  > Time elapsed: {time_at_step} min")
            print(f"  > Start side: {sorted(end_config[0])}")
            print(f"  > End side:   {sorted(end_config[1])}")
            print("-" * 40)
    else:
        print("No solution could be found within the time limit.")


# --- Main Execution Block ---
if __name__ == "__main__":
    CROSSING_TIMES = {
        'Amogh': 5,
        'Ameya': 10,
        'Grandmother': 20,
        'Grandfather': 25
    }
    TIME_LIMIT = 60

    # Solve using BFS (Dijkstra's)
    total_time_bfs, solution_path_bfs, visited_times_bfs_map = solve_bridge_problem_bfs(CROSSING_TIMES, TIME_LIMIT)
    print_bridge_solution(total_time_bfs, solution_path_bfs, CROSSING_TIMES, visited_times_bfs_map, "BFS (Dijkstra's)")

    # Solve using DFS
    total_time_dfs, solution_path_dfs, visited_times_dfs_map = solve_bridge_problem_dfs(CROSSING_TIMES, TIME_LIMIT)
    print_bridge_solution(total_time_dfs, solution_path_dfs, CROSSING_TIMES, visited_times_dfs_map, "DFS (with Optimization)")
