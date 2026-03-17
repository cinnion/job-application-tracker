'use strict';
const webpack = require('webpack');
const path = require('path');
const autoprefixer = require('autoprefixer');
const BundleTracker = require('webpack-bundle-tracker');

const config = {
    entry: {
        bundle: [path.resolve(__dirname, 'static/js/index.jsx')],
//        application_details: [path.resolve(__dirname, 'applications', 'static/applications/js/details.jsx')]
    },
    output: {
        path: path.resolve(__dirname, 'static/webpack_bundles'),
        filename: '[name]-[fullhash].js',
    },
    module: {
        rules: [
            {
                test: /\.css$/i,
                use: [
                    'style-loader',
                    'css-loader'
                ]
            },
            {
                test: /\.s[ac]ss$/i,
                use: [
                    { loader: 'style-loader' },
                    { loader: 'css-loader' },
                    {
                        loader: 'postcss-loader',
                        options: {
                            postcssOptions: {
                                plugins: [ autoprefixer ]
                            }
                        }
                    },
                    { loader: 'sass-loader' },
                ]
            }
        ]
    },
    resolve: {
        alias: {
            '@applications_static': path.resolve(__dirname, 'applications/static/applications'),
        },
        extensions: ['.js', '.jsx', '.css']
    },
    plugins: [
        new BundleTracker({filename: 'webpack-stats.json'}),
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery',
            'window.jQuery': 'jquery'
        })
    ]
};

module.exports = config;
