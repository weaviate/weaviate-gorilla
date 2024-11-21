# Experiment Results

## Overall Performance Comparison

\begin{table}[h]
\centering
\begin{tabular}{|l|r|r|}
\hline
\textbf{Metric} & \textbf{GPT-4o} & \textbf{GPT-4o-mini} \\
\hline
Total Queries & 315 & 315 \\
Successful Predictions & 304 & 308 \\
Failed Predictions & 11 & 7 \\
Average AST Score & 85.66\% & 83.43\% \\
\hline
\end{tabular}
\caption{Overall Performance Metrics}
\label{tab:overall-performance}
\end{table}

## Per Schema Performance

\begin{table}[h]
\centering
\begin{tabular}{|l|r|r|}
\hline
\textbf{Schema} & \textbf{GPT-4o} & \textbf{GPT-4o-mini} \\
\hline
Schema 0 & 87.97\% & 84.14\% \\
Schema 1 & 85.59\% & 84.10\% \\
Schema 2 & 85.08\% & 82.30\% \\
Schema 3 & 81.45\% & 82.23\% \\
Schema 4 & 82.62\% & 79.18\% \\
\hline
\end{tabular}
\caption{Performance Across Different Schemas}
\label{tab:schema-performance}
\end{table}

## Component Analysis

\begin{table}[h]
\centering
\begin{tabular}{|l|r|r|r|}
\hline
\textbf{Component Type} & \textbf{Sample Size} & \textbf{GPT-4o} & \textbf{GPT-4o-mini} \\
\hline
Search Queries & 160 & 76.77\% & 72.48\% \\
Integer Filters & 80 & 79.28\% & 76.31\% \\
Text Filters & 80 & 84.53\% & 85.16\% \\
Boolean Filters & 80 & 91.44\% & 88.13\% \\
Integer Aggregations & 80 & 82.38\% & 82.69\% \\
Text Aggregations & 80 & 83.16\% & 78.78\% \\
Boolean Aggregations & 80 & 87.03\% & 84.59\% \\
GroupBy Operations & 160 & 83.53\% & 80.03\% \\
\hline
\end{tabular}
\caption{Performance Analysis by Component Type}
\label{tab:component-analysis}
\end{table}

# Latex

![Weaviate Gorilla](../../visuals/weaviate-gorillas/gorilla-118.png)
