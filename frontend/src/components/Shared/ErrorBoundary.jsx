import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 m-2 border border-rose-400 rounded-2xl bg-rose-50 text-rose-800 dark:bg-rose-950 dark:border-rose-900 dark:text-rose-200 text-sm">
          <h3 className="text-base font-semibold mb-2">Component Failed to Render</h3>
          <p className="mb-4 opacity-80">
            {this.state.error?.message || "An unexpected error occurred in this section."}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="px-4 py-2 bg-rose-600 text-white font-semibold rounded-xl hover:bg-rose-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;