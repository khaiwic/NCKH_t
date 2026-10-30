#include <iostream>
#include <vector>
#include <queue>
#include <functional>
#include <limits>
using namespace std;

using ll = long long;
using Edge = pair<int, ll>;

const ll INF = numeric_limits<ll>::max();

vector<ll> dijkstra(int s, const vector<vector<Edge>>& graph) {
    vector<ll> dist(graph.size(), INF);

    priority_queue<pair<ll, int>,
                   vector<pair<ll, int>>,
                   greater<pair<ll, int>>> pq;

    dist[s] = 0;
    pq.push({0, s});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();

        if (d != dist[u]) continue;

        for (auto [v, w] : graph[u]) {
            if (d <= INF - w && d + w < dist[v]) {
                dist[v] = d + w;
                pq.push({dist[v], v});
            }
        }
    }

    return dist;
}

void printResult(int s, const vector<ll>& dist) {
    for (int v = 1; v < static_cast<int>(dist.size()); ++v) {
        cout << s << " -> " << v << ": ";

        if (dist[v] == INF)
            cout << "Khong co duong di\n";
        else
            cout << dist[v] << '\n';
    }
}

void run() {
    int n, m, s;
    cin >> n >> m >> s;

    vector<vector<Edge>> graph(n + 1);

    for (int i = 0; i < m; ++i) {
        int u, v;
        ll w;
        cin >> u >> v >> w;

        if (w < 0) {
            cerr << "Dijkstra yeu cau trong so khong am.\n";
            return;
        }

        graph[u].push_back({v, w});
        graph[v].push_back({u, w});
    }

    vector<ll> dist = dijkstra(s, graph);
    printResult(s, dist);
}

int main() {
    run();
}