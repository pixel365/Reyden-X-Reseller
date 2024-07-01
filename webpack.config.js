// Generated using webpack-cli https://github.com/webpack/webpack-cli

const path = require('path');
const {CleanWebpackPlugin} = require('clean-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const autoprefixer = require('autoprefixer');
const TerserPlugin = require('terser-webpack-plugin');
const RemoveEmptyScriptsPlugin = require('webpack-remove-empty-scripts');

const Rules = {
    Scss: {
        test: /\.scss$/i,
        exclude: path.resolve(__dirname, 'node_modules'),
        use: [
            {
                loader: MiniCssExtractPlugin.loader,
            },
            {
                loader: 'css-loader',
                options: {
                  sourceMap: false,
                },
            },
            {
               loader: 'postcss-loader',
               options: {
                   postcssOptions: {
                       plugins: [
                        autoprefixer(),
                       ],
                       sourceMap: false
                   }
               },
            },
            'sass-loader'                
        ],
    },
    Ts: {
        test: /\.(ts|tsx)$/i,
        exclude: path.resolve(__dirname, 'node_modules'),
        loader: 'ts-loader',
    }
}

module.exports = [
    {
        //internal
        entry: {
            style: {
                import: path.resolve(__dirname, 'internal/src/scss/index.scss'),
            },
            script: {
                import: path.resolve(__dirname, 'internal/src/ts/index.ts'),
                filename: './script.js',
            }
        },
        output: {
            path: path.resolve(__dirname, 'static/internal'),
        },
        plugins: [
            new CleanWebpackPlugin(),
            new RemoveEmptyScriptsPlugin(),
            new MiniCssExtractPlugin({
                filename: './[name].css',
            }),
        ],
        module: {
            rules: [
                Rules.Scss,
                Rules.Ts,
            ]
        },
        resolve: {
            extensions: ['.tsx', '.ts', '.js', '.scss'],
        },
        optimization: {
            minimize: true,
            minimizer: [
                new TerserPlugin({
                    terserOptions: {
                        keep_classnames: true,
                        keep_fnames: true,
                        ie8: true,
                        safari10: true,
                    }
                })
            ]
        }
    },
    {
        //unauthenticated
        entry: {
            style: {
                import: path.resolve(__dirname, 'unauthenticated/src/scss/index.scss'),
            }
        },
        output:{
            path: path.resolve(__dirname, 'static/unauthenticated'),
        },
        plugins:[
            new CleanWebpackPlugin(),
            new RemoveEmptyScriptsPlugin(),
            new MiniCssExtractPlugin({
                filename: './[name].css',
            }),          
        ],
        module:{
            rules: [
                Rules.Scss,
            ]
        },
        resolve: {
            extensions: ['.scss'],
        }
    }
]
